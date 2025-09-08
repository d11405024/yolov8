from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

# 載入 YOLOv5 模型
model = YOLO('yolov5s.pt')

# 打開影片檔案
video_path = "yolo.mp4"
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

    # 執行 YOLO 追蹤
    # 將 verbose 設定為 False，以隱藏終端機中重複的輸出資訊
    results = model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)

    # 檢查是否有追蹤結果
    if results[0].boxes and results[0].boxes.id is not None:
        boxes = results[0].boxes.xywh.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        confs = results[0].boxes.conf.float().cpu().tolist()
        cls_ids = results[0].boxes.cls.int().cpu().tolist()
        class_names = model.names
        
        # 創建一個畫布來繪圖
        annotated_frame = frame.copy()

        # 遍歷每個追蹤結果
        for i, (box, track_id, conf, cls_id) in enumerate(zip(boxes, track_ids, confs, cls_ids)):
            x, y, w, h = box
            
            # 將中心點坐標添加到追蹤歷史
            track_point = (int(x), int(y))
            track = track_history[track_id]
            track.append(track_point)
            
            # 如果追蹤歷史超過 30 個點，則只保留最新的 30 個
            if len(track) > 30:
                track.pop(0)

            # 繪製追蹤線條 (只有當點數大於2才繪製)
            if len(track) > 2:
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=track_line_color, thickness=2)

            # 繪製偵測框和標籤
            box_top_left = (int(x - w / 2), int(y - h / 2))
            box_bottom_right = (int(x + w / 2), int(y + h / 2))
            cv2.rectangle(annotated_frame, box_top_left, box_bottom_right, box_color, 2)

            label = f"id:{track_id} {class_names[cls_id]} {conf:.2f}"
            text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            text_origin = (box_top_left[0], box_top_left[1] - 10)
            cv2.rectangle(annotated_frame, (text_origin[0], text_origin[1] - text_size[1] - 5), 
                          (text_origin[0] + text_size[0] + 5, text_origin[1]), box_color, -1)
            cv2.putText(annotated_frame, label, text_origin, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # 繪製軌跡點 (粉色實心圓)
            cv2.circle(annotated_frame, track_point, radius=5, color=dot_color, thickness=-1)
        
        # 將處理後的幀寫入影片檔案
        out.write(annotated_frame)
        # 顯示處理後的幀
        cv2.imshow("YOLOv5 Tracking", annotated_frame)
    else:
        # 如果沒有偵測到物件，顯示原始幀並寫入影片
        out.write(frame)
        cv2.imshow("YOLOv5 Tracking", frame)

    # 如果按下 'q' 鍵，則退出迴圈
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 釋放資源
cap.release()
out.release()
cv2.destroyAllWindows()