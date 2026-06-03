import sys
import time
import cv2
import numpy as np

from camera import Camera
from tracker import Tracker
from state_mapper import StateMapper
from profile import Profile
from renderer import Renderer


def main():
    profile_path = sys.argv[1] if len(sys.argv) > 1 else "profiles/vup.json"
    profile = Profile(profile_path)

    try:
        camera = Camera()
    except RuntimeError as e:
        print(f"[VUP] 摄像头错误: {e}")
        print("[VUP] 以无摄像头模式运行（键盘控制）：e/E 眼睛  m/M 嘴巴  r 重置")
        camera = None

    tracker = Tracker()
    mapper = StateMapper(smoothing=0.15)
    kb_eye, kb_mouth = 0.0, 0.0

    try:
        renderer = Renderer(profile)
    except Exception as e:
        print(f"[VUP] 渲染器失败: {e}")
        return

    cv2.namedWindow("VUP Debug", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("VUP Debug", 320, 240)

    debug_open = True

    print(f"[VUP] 启动 | 角色: {profile.name}")
    print(f"[VUP] 布局: {profile.get_layout_width()}x{profile.get_layout_height()}, "
          f"{len(profile.roles)} 个角色")

    try:
        while renderer.is_running():
            frame = None
            eye_vals = mouth_val = None
            face_regions = {}
            hands_data = []

            if camera:
                frame = camera.read()
                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    tracker.process(frame_rgb)
                    eye_vals = tracker.get_eye_openness()
                    mouth_val = tracker.get_mouth_openness()
                    face_regions = tracker.get_face_regions()
                    hands_data = tracker.get_hands_data()

            if not mapper.has_face and not camera:
                mapper.update((kb_eye, kb_eye), kb_mouth, {}, [])
            else:
                mapper.update(eye_vals, mouth_val, face_regions, hands_data)

            renderer.draw(profile, mapper)

            if debug_open:
                try:
                    if cv2.getWindowProperty("VUP Debug", 0) < 0:
                        debug_open = False
                        continue
                except Exception:
                    debug_open = False
                    continue
                dbg = np.zeros((240, 320, 3), dtype=np.uint8)
                if frame is not None:
                    dbg = cv2.resize(frame, (320, 240))
                color = (0, 255, 0) if mapper.has_face else (100, 100, 100)
                cv2.putText(dbg, f"L:{mapper.left_eye_openness:.2f} R:{mapper.right_eye_openness:.2f}", (5, 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1)
                cv2.putText(dbg, f"Mouth:{mapper.mouth_openness:.2f}", (5, 36),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                cv2.putText(dbg, f"Regions:{len(face_regions)}", (5, 54),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                cv2.putText(dbg, f"Hands:{len(hands_data)}", (5, 72),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                cv2.putText(dbg, "Q=close debug", (205, 230),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
                cv2.imshow("VUP Debug", dbg)

                key = cv2.waitKey(1) & 0xFF
                if key in (ord('q'), ord('Q')):
                    cv2.destroyWindow("VUP Debug")
                    debug_open = False
            else:
                time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        if camera:
            camera.release()
        tracker.close()
        renderer.close()
        try:
            cv2.destroyWindow("VUP Debug")
        except Exception:
            pass
        print("[VUP] 已关闭")


if __name__ == "__main__":
    main()
