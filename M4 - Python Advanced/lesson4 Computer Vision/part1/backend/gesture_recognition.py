"""
Utility helpers for detecting rock, paper, scissors hand gestures with MediaPipe.

The module exposes a `HandCaptureSession` class so the FastAPI backend can both
stream annotated preview frames and return the final gesture prediction.
"""

from __future__ import annotations

import threading
import time
from collections import Counter
from typing import Dict, Generator, Optional, Tuple

import cv2
import mediapipe as mp

# MediaPipe landmark indices for the fingers we care about
FINGER_TIPS = [8, 12, 16, 20]
FINGER_PIPS = [6, 10, 14, 18]
THUMB_TIP = 4
THUMB_IP = 3

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles


def _finger_states(hand_landmarks, handedness: str) -> Dict[str, bool]:
    """Determine which fingers are extended for a given set of landmarks."""

    lm = hand_landmarks.landmark

    # For each finger (index to pinky) we look at the vertical relationship
    finger_ups = []
    for tip_index, pip_index in zip(FINGER_TIPS, FINGER_PIPS):
        finger_ups.append(lm[tip_index].y < lm[pip_index].y)

    # Thumb is transversal to the palm, so we use the horizontal axis.
    if handedness.lower() == "right":
        thumb_up = lm[THUMB_TIP].x > lm[THUMB_IP].x
    else:
        thumb_up = lm[THUMB_TIP].x < lm[THUMB_IP].x

    return {
        "thumb": thumb_up,
        "index": finger_ups[0],
        "middle": finger_ups[1],
        "ring": finger_ups[2],
        "pinky": finger_ups[3],
    }


def _classify_move(states: Dict[str, bool]) -> Optional[str]:
    """Convert finger state information into one of our labels."""

    open_fingers = sum(states.values())

    # Rock: everything curled (no finger extended)
    if open_fingers == 0:
        return "rock"

    # Paper: all fingers extended (thumb included)
    if open_fingers == 5:
        return "paper"

    # Scissors: index + middle extended, others curled
    if (
        states["index"]
        and states["middle"]
        and not states["ring"]
        and not states["pinky"]
    ):
        return "scissors"

    return None


class HandCaptureSession:
    """Background MediaPipe capture with optional MJPEG preview streaming."""

    def __init__(
        self,
        capture_seconds: float = 5.0,
        detection_confidence: float = 0.6,
        tracking_confidence: float = 0.5,
    ) -> None:
        self.capture_seconds = capture_seconds
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._finished = threading.Event()
        self._lock = threading.Lock()

        self._latest_frame: Optional[bytes] = None
        self._votes: Counter[str] = Counter()
        self._samples = 0
        self._current_label = "warming up"
        self._result_move = "none"
        self._stats: Dict[str, int] = {"rock": 0, "paper": 0, "scissors": 0, "samples": 0}
        self.error: Optional[RuntimeError] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_capture, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def wait_until_finished(self, timeout: Optional[float] = None) -> None:
        self._finished.wait(timeout=timeout)

    @property
    def is_finished(self) -> bool:
        return self._finished.is_set()

    @property
    def current_label(self) -> str:
        return self._current_label

    def get_result(self) -> Tuple[str, Dict[str, int]]:
        return self._result_move, self._stats

    def iter_preview_frames(self) -> Generator[bytes, None, None]:
        """Yield MJPEG chunks until the capture session finishes."""

        boundary = b"--frame"
        while not self.is_finished:
            with self._lock:
                frame = self._latest_frame
            if frame:
                yield boundary + b"\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            time.sleep(0.05)
        with self._lock:
            frame = self._latest_frame
        if frame:
            yield boundary + b"\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

    # --- Internal helpers -------------------------------------------------

    def _run_capture(self) -> None:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.error = RuntimeError("Could not access the webcam. Is it connected and free?")
            self._finished.set()
            return

        start_ts = time.time()

        with mp_hands.Hands(
            model_complexity=0,
            max_num_hands=1,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence,
        ) as hands:
            while not self._stop.is_set() and time.time() - start_ts < self.capture_seconds:
                success, frame = cap.read()
                if not success:
                    continue

                frame = cv2.flip(frame, 1)  # Mirror for a more natural student experience
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                annotated = frame.copy()
                detected_move: Optional[str] = None

                if results.multi_hand_landmarks:
                    for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        hand_label = "right"
                        if results.multi_handedness:
                            hand_label = (
                                results.multi_handedness[idx].classification[0]
                                .label.lower()
                            )

                        states = _finger_states(hand_landmarks, hand_label)
                        move = _classify_move(states)
                        if move:
                            detected_move = move
                            self._votes[move] += 1

                        mp_drawing.draw_landmarks(
                            annotated,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_styles.get_default_hand_landmarks_style(),
                            mp_styles.get_default_hand_connections_style(),
                        )
                else:
                    detected_move = None

                if detected_move:
                    self._current_label = detected_move
                else:
                    self._current_label = "searching"

                self._samples += 1
                self._stats = {
                    "rock": self._votes["rock"],
                    "paper": self._votes["paper"],
                    "scissors": self._votes["scissors"],
                    "samples": self._samples,
                }

                overlay = f"Gesture: {self._current_label.upper()}"
                cv2.putText(
                    annotated,
                    overlay,
                    (16, 42),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0) if detected_move else (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                votes_overlay = (
                    f"Votes ? R:{self._votes['rock']} P:{self._votes['paper']} S:{self._votes['scissors']}"
                )
                cv2.putText(
                    annotated,
                    votes_overlay,
                    (16, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (200, 200, 200),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    annotated,
                    "Hold your gesture steady!",
                    (16, annotated.shape[0] - 24),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                success, buffer = cv2.imencode(".jpg", annotated)
                if success:
                    with self._lock:
                        self._latest_frame = buffer.tobytes()

                time.sleep(0.03)

        cap.release()

        if self._votes:
            self._result_move, _ = self._votes.most_common(1)[0]
        else:
            self._result_move = "none"

        self._finished.set()


def detect_hand_move(
    capture_seconds: float = 5.0,
    detection_confidence: float = 0.6,
    tracking_confidence: float = 0.5,
) -> Tuple[str, Dict[str, int]]:
    """Legacy helper that blocks until a capture session finishes."""

    session = HandCaptureSession(
        capture_seconds=capture_seconds,
        detection_confidence=detection_confidence,
        tracking_confidence=tracking_confidence,
    )
    session.start()
    session.wait_until_finished()

    if session.error:
        raise session.error

    return session.get_result()


__all__ = ["HandCaptureSession", "detect_hand_move"]
