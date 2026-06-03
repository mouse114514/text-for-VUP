import cv2


class Camera:
    def __init__(self, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"无法打开摄像头 {camera_id}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.flip(frame, 1)

    def release(self):
        self.cap.release()
