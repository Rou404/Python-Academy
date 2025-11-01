"""
Continuous camera monitor providing MJPEG preview and live gesture/expression labels.

The monitor keeps a single MediaPipe pipeline alive so the backend can
stream annotated frames to the React dashboard, compute majority votes for
rock/paper/scissors rounds, and aggregate facial expressions without fighting
for webcam access.
"""

from __future__ import annotations

import threading
import time
from collections import Counter
from typing import Dict, Generator, Optional, Tuple

import cv2
import mediapipe as mp

from expression_recognition import classify_expression_from_landmarks
from gesture_recognition import _finger_states, _classify_move  # type: ignore

MOVES = ("rock", "paper", "scissors")


class VisionMonitor:
    """Singleton-style helper that keeps a shared camera capture running."""

    def __init__(self) -> None:
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._ready = threading.Event()
        self.error: Optional[RuntimeError] = None

        self._lock = threading.Lock()
        self._latest_frame: Optional[bytes] = None
        self._gesture_label = "searching"
        self._expression_label = "neutral"

        # Round-specific bookkeeping
        self._round_lock = threading.Lock()
        self._round_active = False
        self._round_end_time = 0.0
        self._round_votes: Counter[str] = Counter()
        self._round_samples = 0
        self._round_result: Tuple[str, Dict[str, int]] = (
            "none",
            {"rock": 0, "paper": 0, "scissors": 0, "samples": 0},
        )
        self._round_event = threading.Event()

        # Expression aggregation bookkeeping
        self._expression_lock = threading.Lock()
        self._expression_active = False
        self._expression_end_time = 0.0
        self._expression_votes: Counter[str] = Counter()
        self._expression_samples = 0
        self._expression_result: Tuple[str, Dict[str, float]] = (
            "neutral",
            {"samples": 0, "confidence": 0.0},
        )
        self._expression_event = threading.Event()

    # ------------------------------------------------------------------
    # Public API
    def ensure_started(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self.error = None
        self._ready.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5.0)
        if self.error:
            raise self.error

    def iter_preview_frames(self) -> Generator[bytes, None, None]:
        self.ensure_started()
        boundary = b"--frame"
        while not self._stop.is_set():
            if self.error:
                break
            with self._lock:
                frame = self._latest_frame
            if frame:
                yield boundary + b"\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            time.sleep(0.05)

    def get_labels(self) -> Dict[str, object]:
        self.ensure_started()
        with self._lock:
            gesture = self._gesture_label
            expression = self._expression_label
        return {
            "gesture_label": gesture,
            "expression_label": expression,
            "timestamp": time.time(),
        }

    def start_round(self, duration: float = 5.0) -> None:
        self.ensure_started()
        with self._round_lock:
            if self._round_active:
                raise RuntimeError("A round capture is already running.")
            self._round_active = True
            self._round_end_time = time.time() + duration
            self._round_votes = Counter()
            self._round_samples = 0
            self._round_result = (
                "none",
                {"rock": 0, "paper": 0, "scissors": 0, "samples": 0},
            )
            self._round_event.clear()

    def wait_round_result(self, timeout: Optional[float] = None) -> Tuple[str, Dict[str, int]]:
        if not self._round_event.wait(timeout):
            raise TimeoutError("Timed out while waiting for the round to finish")
        with self._round_lock:
            result = self._round_result
            self._round_event.clear()
            self._round_active = False
        return result

    def cancel_round(self) -> None:
        with self._round_lock:
            self._round_active = False
            self._round_event.clear()
            self._round_votes = Counter()
            self._round_samples = 0
            self._round_result = (
                "none",
                {"rock": 0, "paper": 0, "scissors": 0, "samples": 0},
            )

    def start_expression_capture(self, duration: float = 4.0) -> None:
        self.ensure_started()
        with self._expression_lock:
            if self._expression_active:
                raise RuntimeError("Expression capture already running.")
            self._expression_active = True
            self._expression_end_time = time.time() + duration
            self._expression_votes = Counter()
            self._expression_samples = 0
            self._expression_result = ("neutral", {"samples": 0, "confidence": 0.0})
            self._expression_event.clear()

    def wait_expression_result(self, timeout: Optional[float] = None) -> Tuple[str, Dict[str, float]]:
        if not self._expression_event.wait(timeout):
            raise TimeoutError("Timed out while waiting for expression capture")
        with self._expression_lock:
            result = self._expression_result
            self._expression_event.clear()
            self._expression_active = False
        return result

    # ------------------------------------------------------------------
    def _capture_loop(self) -> None:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.error = RuntimeError("Could not access the webcam. Is it connected and free?")
            self._ready.set()
            return

        mp_hands = mp.solutions.hands.Hands(
            model_complexity=0,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        mp_face = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        drawing = mp.solutions.drawing_utils
        styles = mp.solutions.drawing_styles

        self._ready.set()

        try:
            while not self._stop.is_set():
                success, frame = cap.read()
                if not success:
                    continue

                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Hand processing
                hand_results = mp_hands.process(rgb)
                gesture_label = "searching"
                if hand_results.multi_hand_landmarks:
                    for idx, hand_landmarks in enumerate(hand_results.multi_hand_landmarks):
                        handedness = "right"
                        if hand_results.multi_handedness:
                            handedness = (
                                hand_results.multi_handedness[idx].classification[0]
                                .label.lower()
                            )
                        states = _finger_states(hand_landmarks, handedness)
                        move = _classify_move(states)
                        if move:
                            gesture_label = move
                        drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp.solutions.hands.HAND_CONNECTIONS,
                            styles.get_default_hand_landmarks_style(),
                            styles.get_default_hand_connections_style(),
                        )
                else:
                    gesture_label = "searching"

                self._update_round_stats(gesture_label)

                # Face processing
                expression_label = "no face"
                face_results = mp_face.process(rgb)
                if face_results.multi_face_landmarks:
                    face_landmarks = face_results.multi_face_landmarks[0].landmark
                    expression_label, _ = classify_expression_from_landmarks(face_landmarks)

                self._update_expression_stats(expression_label)

                # Store latest labels for status endpoint
                with self._lock:
                    self._gesture_label = gesture_label
                    self._expression_label = expression_label

                overlay = frame.copy()
                cv2.putText(
                    overlay,
                    f"Gesture: {gesture_label.upper()}",
                    (16, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0) if gesture_label in MOVES else (200, 200, 200),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    overlay,
                    f"Expression: {expression_label.upper()}",
                    (16, 78),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 215, 0) if expression_label == "happy" else (200, 200, 200),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    overlay,
                    "Camera is live. Use the buttons to trigger game rounds.",
                    (16, overlay.shape[0] - 24),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (220, 220, 220),
                    2,
                    cv2.LINE_AA,
                )

                success, buffer = cv2.imencode(".jpg", overlay)
                if success:
                    with self._lock:
                        self._latest_frame = buffer.tobytes()

                time.sleep(0.03)
        finally:
            mp_hands.close()
            mp_face.close()
            cap.release()

    # ------------------------------------------------------------------
    def _update_round_stats(self, gesture_label: str) -> None:
        with self._round_lock:
            if not self._round_active:
                return
            self._round_samples += 1
            if gesture_label in MOVES:
                self._round_votes[gesture_label] += 1
            if time.time() >= self._round_end_time:
                if self._round_votes:
                    move, _ = self._round_votes.most_common(1)[0]
                else:
                    move = "none"
                stats = {
                    "rock": self._round_votes["rock"],
                    "paper": self._round_votes["paper"],
                    "scissors": self._round_votes["scissors"],
                    "samples": self._round_samples,
                }
                self._round_result = (move, stats)
                self._round_active = False
                self._round_event.set()

    def _update_expression_stats(self, expression_label: str) -> None:
        clean_label = expression_label if expression_label in {"happy", "sad", "angry", "neutral"} else None
        with self._expression_lock:
            if not self._expression_active:
                return
            self._expression_samples += 1
            if clean_label:
                self._expression_votes[clean_label] += 1
            if time.time() >= self._expression_end_time:
                if self._expression_votes:
                    label, count = self._expression_votes.most_common(1)[0]
                    confidence = count / max(self._expression_samples, 1)
                else:
                    label = "neutral"
                    confidence = 0.0
                self._expression_result = (label, {
                    "samples": self._expression_samples,
                    "confidence": confidence,
                })
                self._expression_active = False
                self._expression_event.set()


monitor = VisionMonitor()


__all__ = ["VisionMonitor", "monitor"]
