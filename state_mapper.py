import numpy as np


class StateMapper:
    def __init__(self, smoothing=0.15):
        self.smoothing = smoothing

        self.eye_openness = 0.0
        self.left_eye_openness = 0.0
        self.right_eye_openness = 0.0
        self.mouth_openness = 0.0
        self.has_face = False

        self.face_regions = {}
        self.hands_data = []

        self.smoothed_regions = {}

    def update(self, eye_vals, mouth_val, face_regions, hands_data):
        self.has_face = eye_vals is not None and eye_vals[0] is not None
        self.hands_data = hands_data
        self.face_regions = face_regions

        if eye_vals is not None and eye_vals[0] is not None:
            left, right = eye_vals
            self.left_eye_openness += (left - self.left_eye_openness) * (1 - self.smoothing)
            self.right_eye_openness += (right - self.right_eye_openness) * (1 - self.smoothing)
            self.eye_openness = (self.left_eye_openness + self.right_eye_openness) / 2.0
        else:
            self.left_eye_openness += (0.5 - self.left_eye_openness) * 0.02
            self.right_eye_openness += (0.5 - self.right_eye_openness) * 0.02
            self.eye_openness = (self.left_eye_openness + self.right_eye_openness) / 2.0

        if mouth_val is not None:
            self.mouth_openness += (mouth_val - self.mouth_openness) * (1 - self.smoothing)
        else:
            self.mouth_openness += (0.0 - self.mouth_openness) * 0.02

        for key, region in face_regions.items():
            if key not in self.smoothed_regions:
                self.smoothed_regions[key] = {"cx": 0.5, "cy": 0.5, "size": 0.1}
            s = self.smoothed_regions[key]
            s["cx"] += (region["cx"] - s["cx"]) * 0.3
            s["cy"] += (region["cy"] - s["cy"]) * 0.3
            s["size"] += (region["size"] - s["size"]) * 0.3

    def get_part_state(self, role_type, role_name=""):
        if role_type == "eye":
            if "左" in role_name or role_name.lower().startswith("left"):
                return self.left_eye_openness
            if "右" in role_name or role_name.lower().startswith("right"):
                return self.right_eye_openness
            return min(self.left_eye_openness, self.right_eye_openness)
        elif role_type == "mouth":
            return self.mouth_openness
        return 0.5

    def get_part_transform(self, role_type, side=""):
        base_scale = 1.0
        dx, dy = 0.0, 0.0

        if role_type == "eye":
            r = self.smoothed_regions.get("eye")
            if r:
                dx = (r["cx"] - 0.5) * 300
                dy = (r["cy"] - 0.5) * 200
                base_scale = 0.6 + r["size"] * 3.0
        elif role_type == "mouth":
            r = self.smoothed_regions.get("mouth")
            if r:
                dx = (r["cx"] - 0.5) * 300
                dy = (r["cy"] - 0.5) * 200
                base_scale = 0.6 + r["size"] * 3.0
        elif role_type == "nose":
            r = self.smoothed_regions.get("nose")
            if r:
                dx = (r["cx"] - 0.5) * 300
                dy = (r["cy"] - 0.5) * 200
                base_scale = 0.6 + r["size"] * 3.0
        elif role_type == "hand" and side:
            for h in self.hands_data:
                if h.get("side") == side:
                    dx = (h["cx"] - 0.5) * 400
                    dy = (h["cy"] - 0.5) * 300
                    base_scale = 0.5 + h["size"] * 3.0
                    break
        elif role_type == "body" or role_type == "face":
            r = self.smoothed_regions.get("face")
            if r:
                dx = (r["cx"] - 0.5) * 300
                dy = (r["cy"] - 0.5) * 200
                base_scale = 0.6 + r["size"] * 3.0

        return {
            "offset_x": dx,
            "offset_y": dy,
            "scale": base_scale,
        }

    def get_part_transform_for_role(self, profile_role):
        return self.get_part_transform(profile_role.type, profile_role.side)
