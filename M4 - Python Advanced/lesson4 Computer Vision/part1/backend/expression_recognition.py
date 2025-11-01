"""
Facial expression recognition helpers powered by MediaPipe Face Mesh.

The heuristics implemented here keep the math intentionally lightweight so the
workflow remains approachable for students during the course demo.
"""

from __future__ import annotations

import math
import time
from collections import Counter
from typing import Dict, Tuple

import cv2
import mediapipe as mp

# Landmark indices we use frequently when building the facial metrics
FACE_IDX = {
    "nose_tip": 1,
    "chin": 152,
    "mouth_left": 61,
    "mouth_right": 291,
    "mouth_top": 13,
    "mouth_bottom": 14,
    "brow_left_inner": 70,
    "brow_right_inner": 300,
    "brow_left_outer": 105,
    "brow_right_outer": 334,
}


def _distance(landmarks, point_a: str, point_b: str) -> float:
    """Euclidean distance between two selected landmarks."""

    a = landmarks[FACE_IDX[point_a]]
    b = landmarks[FACE_IDX[point_b]]
    return math.sqrt(
        (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2
    )


def _compute_metrics(landmarks) -> Dict[str, float]:
    """Extract a couple of interpretable facial action metrics."""

    chin_span = _distance(landmarks, "nose_tip", "chin") + 1e-6
    mouth_width = _distance(landmarks, "mouth_left", "mouth_right")
    mouth_open = _distance(landmarks, "mouth_top", "mouth_bottom")
    brow_gap = _distance(landmarks, "brow_left_inner", "brow_right_inner")
    brow_span = _distance(landmarks, "brow_left_outer", "brow_right_outer") + 1e-6

    mouth_left = landmarks[FACE_IDX["mouth_left"]]
    mouth_right = landmarks[FACE_IDX["mouth_right"]]
    lip_mid = (mouth_left.y + mouth_right.y) / 2
    upper_lip = landmarks[FACE_IDX["mouth_top"]].y

    return {
        "smile": mouth_width / chin_span,
        "mouth_open": mouth_open / chin_span,
        "brow_furrow": brow_gap / brow_span,
        "lip_curl": lip_mid - upper_lip,
    }


def _classify_expression(metrics: Dict[str, float]) -> str:
    """Map our heuristic metrics to a coarse emotion label."""

    smile = metrics["smile"]
    mouth_open = metrics["mouth_open"]
    brow_furrow = metrics["brow_furrow"]
    lip_curl = metrics["lip_curl"]

    if smile > 0.52 and mouth_open > 0.04:
        return "happy"

    if brow_furrow < 0.42 and mouth_open < 0.035:
        return "angry"

    if lip_curl > 0.02 and mouth_open < 0.045:
        return "sad"

    return "neutral"


def classify_expression_from_landmarks(landmarks) -> Tuple[str, Dict[str, float]]:
    """Return the expression label and raw metrics for a set of landmarks."""

    metrics = _compute_metrics(landmarks)
    label = _classify_expression(metrics)
    return label, metrics


def detect_expression(
    capture_seconds: float = 4.0,
    detection_confidence: float = 0.5,
    tracking_confidence: float = 0.5,
) -> Tuple[str, Dict[str, float]]:
    """
    Observe the webcam for a short interval and return the dominant expression.

    Returns
    -------
    expression : str
        One of "happy", "sad", "angry", or "neutral".
    stats : dict
        Aggregated metrics so the caller can surface debugging insights.
    """

    mp_face_mesh = mp.solutions.face_mesh
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        raise RuntimeError("Could not access the webcam for expression capture.")

    votes: Counter[str] = Counter()
    samples = 0
    start_ts = time.time()

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=detection_confidence,
        min_tracking_confidence=tracking_confidence,
    ) as face_mesh:
        while time.time() - start_ts < capture_seconds:
            success, frame = cap.read()
            if not success:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if not results.multi_face_landmarks:
                continue

            samples += 1
            face_landmarks = results.multi_face_landmarks[0].landmark
            metrics = _compute_metrics(face_landmarks)
            expression = _classify_expression(metrics)
            votes[expression] += 1

    cap.release()

    if not votes:
        return "neutral", {"samples": samples, "details": {}}

    expression, count = votes.most_common(1)[0]
    confidence = count / max(samples, 1)
    stats = {"samples": samples, "confidence": confidence}
    return expression, stats


__all__ = ["detect_expression", "classify_expression_from_landmarks"]
