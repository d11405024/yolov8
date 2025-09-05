3. **使用指令行轉換模型**：在 Jetson Nano 的終端機中，切換到您存放模型的資料夾，然後執行以下指令：
    
    ```bash
    yolo export model=yolov8n.pt format=engine
    ```
    
    這行指令會將您原本的 `yolov8n.pt` 檔轉換為 `yolov8n.engine` 檔。這個 `.engine` 檔就是經過 TensorRT 優化後的模型，專門為您的 Jetson GPU 所設計。
    
    - **使用 TensorRT 模型進行推理**：當 `.engine` 檔案生成後，您就可以用它來進行推理測試了。
        
        ```bash
        yolo predict model=yolov8n.engine source='your_video.mp4'
        ```
