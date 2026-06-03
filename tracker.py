import os
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.image import Image


MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
FACE_MODEL = os.path.join(MODEL_DIR, "face_landmarker_v2.task")
HAND_MODEL = os.path.join(MODEL_DIR, "hand_landmarker.task")


def _norm_dist(a, b):
    return np.linalg.norm(np.array([a.x, a.y]) - np.array([b.x, b.y]))


def _center(lm, idxs):
    xs = [lm[i].x for i in idxs]
    ys = [lm[i].y for i in idxs]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


# Face landmark indices for each region
REGION_LANDMARKS = {
    "left_eye":   [33, 133],
    "right_eye":  [362, 263],
    "eye":        [33, 133, 362, 263],
    "mouth":      [61, 291],
    "nose":       [1, 2, 98, 327],
    "face":       [10, 152],
}


class Tracker:
    def __init__(self):
        face_options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=FACE_MODEL),
            running_mode=RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
        )
        self.face_landmarker = FaceLandmarker.create_from_options(face_options)

        hand_options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=HAND_MODEL),
            running_mode=RunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.hand_landmarker = HandLandmarker.create_from_options(hand_options)

        self.face_result = None
        self.hand_result = None

    def process(self, frame_rgb):
        mp_image = Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        self.face_result = self.face_landmarker.detect(mp_image)
        self.hand_result = self.hand_landmarker.detect(mp_image)

    def get_eye_openness(self):
        """Returns (left_openness, right_openness) tuple, or (None, None)."""
        if not self.face_result or not self.face_result.face_landmarks:
            return None, None
        lm = self.face_result.face_landmarks[0]
        left = _norm_dist(lm[159], lm[145]) / (_norm_dist(lm[33], lm[133]) + 1e-6)
        right = _norm_dist(lm[386], lm[374]) / (_norm_dist(lm[362], lm[263]) + 1e-6)
        return np.clip((left - 0.03) * 4, 0, 1), np.clip((right - 0.03) * 4, 0, 1)

    def get_mouth_openness(self):
        if not self.face_result or not self.face_result.face_landmarks:
            return None
        lm = self.face_result.face_landmarks[0]
        vert = _norm_dist(lm[13], lm[14])
        horiz = _norm_dist(lm[61], lm[291])
        mar = vert / (horiz + 1e-6)
        return np.clip(mar * 5, 0.0, 1.0)

    def get_face_regions(self):
        if not self.face_result or not self.face_result.face_landmarks:
            return {}
        lm = self.face_result.face_landmarks[0]
        regions = {}
        for name, idxs in REGION_LANDMARKS.items():
            cx, cy = _center(lm, idxs)
            size = 0.0
            if len(idxs) >= 2:
                pts = [lm[i] for i in idxs]
                w = max(p.x for p in pts) - min(p.x for p in pts)
                h = max(p.y for p in pts) - min(p.y for p in pts)
                size = max(w, h)
            regions[name] = {"cx": cx, "cy": cy, "size": size}
        return regions

    def get_hands_data(self):
        if not self.hand_result or not self.hand_result.hand_landmarks:
            return []
        data = []
        for i, hand_lm in enumerate(self.hand_result.hand_landmarks):
            xs = [lm.x for lm in hand_lm]
            ys = [lm.y for lm in hand_lm]
            cx = (min(xs) + max(xs)) / 2
            cy = (min(ys) + max(ys)) / 2
            size = max(max(xs) - min(xs), max(ys) - min(ys))
            side = "unknown"
            if self.hand_result.handedness and i < len(self.hand_result.handedness):
                side = self.hand_result.handedness[i][0].category_name.lower()
            data.append({"cx": cx, "cy": cy, "size": size, "side": side})
        return data

    def close(self):
        self.face_landmarker.close()
        self.hand_landmarker.close()
