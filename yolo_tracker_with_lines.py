from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

# 載入 YOLOv8 模型
model = YOLO('yolov8n.pt')

# 打開影片檔案
video_path = "yolo36.mp4"
cap = cv2.VideoCapture(video_path)

# 儲存追蹤歷史
track_history = defaultdict(lambda: [])

# 定義顏色 (BGR 格式)
track_line_color = (0, 255, 255)  # 亮黃色
box_color = (255, 0, 255)         # 亮粉色
dot_color = (255, 0, 255)         # 亮粉色

# 設定影片寫入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output_final_optimized.mp4', fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))

# 迴圈處理影片的每一幀
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # 執行 YOLOv8 追蹤
    results = model.track(frame, persist=True, tracker="bytetrack.yaml")

    # 檢查是否有追蹤結果
    if results[0].boxes and results[0].boxes.id is not None:
        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        class_names = results[0].names
        cls = results[0].boxes.cls.int().cpu().tolist()
        confs = results[0].boxes.conf.cpu().tolist()

        # 創建一個畫布來繪圖
        annotated_frame = frame.copy()

        # 繪製追蹤軌跡和資訊
        for i, (box, track_id, cls_id) in enumerate(zip(boxes, track_ids, cls)):
            x, y, w, h = box
            
            # 使用偵測框的水平中心點作為軌跡點
            track_point = (int(x), int(y))
            track = track_history[track_id]
            track.append(track_point)

            # 控制軌跡線長度 (例如只保留最近 30 幀)
            if len(track) > 30:
                track.pop(0)

            # 只有當軌跡點數量足夠時才繪製線條
            if len(track) > 5:
                points = np.array(track, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=track_line_color, thickness=2)

            # 繪製偵測框和標籤
            box_top_left = (int(x - w / 2), int(y - h / 2))
            box_bottom_right = (int(x + w / 2), int(y + h / 2))
            cv2.rectangle(annotated_frame, box_top_left, box_bottom_right, box_color, 2)

            label = f"id:{track_id} {class_names[cls_id]} {confs[i]:.2f}"
            text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            text_origin = (box_top_left[0], box_top_left[1] - 10)
            cv2.rectangle(annotated_frame, (text_origin[0], text_origin[1] - text_size[1] - 5), 
                          (text_origin[0] + text_size[0] + 5, text_origin[1]), box_color, -1)
            cv2.putText(annotated_frame, label, text_origin, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # 繪製軌跡點 (粉紅色圓點)
            cv2.circle(annotated_frame, track_point, radius=5, color=dot_color, thickness=-1)

        # 顯示和保存結果
        cv2.imshow("YOLOv8 Optimized Tracking", annotated_frame)
        out.write(annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # 如果這一幀沒有偵測到任何物件，則直接寫入和顯示原始幀
        out.write(frame)
        cv2.imshow("YOLOv8 Optimized Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# 釋放資源並關閉視窗
cap.release()
out.release()
cv2.destroyAllWindows()