Jetson Nano部屬教學
### 步驟一：在 Jetson Nano 上準備環境

Jetson Nano 的環境配置與 PC 上的 Anaconda 環境不同。我們需要手動安裝所有必要的套件。

1. **安裝依賴套件**：打開 Jetson Nano 的終端機，執行以下指令，安裝一些基本的開發工具和函式庫。
    
    ```bash
    sudo apt-get update
    sudo apt-get install git python3-pip
    ```
    
2. **安裝 PyTorch 和 Torchvision**：這是最重要的步驟。由於 Jetson Nano 的特殊架構（ARM），我們不能直接用 `pip` 安裝 PyTorch。需要從 PyTorch 官方網站下載預先編譯好的 `.whl` 檔案來安裝。
    - **下載 PyTorch**：根據 JetPack 版本，找到對應的 PyTorch `.whl` 檔案。通常 PyTorch 官網會有 Jetson 專區。
    - **安裝 PyTorch**：下載後，在終端機中導航到檔案位置，並執行：
        
        ```bash
        sudo pip3 install torch-*.whl
        ```
        
    - **安裝 Torchvision**：Torchvision 需要從原始碼編譯安裝，這需要一些時間。
        
        ```bash
        sudo apt-get install libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev
        git clone --branch v0.14.0 https://github.com/pytorch/vision torchvision
        cd torchvision
        sudo python3 setup.py install
        cd ..
        ```
        
3. **安裝 Ultralytics**：現在您可以安裝 Ultralytics 套件，它會自動安裝其他必要套件。
    
    ```bash
    sudo pip3 install ultralytics
    ```
    

### 步驟二：在 Jetson Nano 上執行 TensorRT 轉換

檔案傳輸完成後，請在 Jetson Nano 的終端機中進行操作。

1. **進入檔案目錄**：Bash
    
    `cd /home/jetson`
    
2. **執行轉換指令**：現在你可以執行我們之前討論的指令了。這個過程會使用 Jetson Nano 上的 GPU 和 TensorRT 函式庫，將模型轉換為 `.engine` 檔。Bash
    
    `yolo export model=yolov8n.pt format=engine`
    
    轉換完成後，你會在同一個目錄下看到一個名為 `yolov8n.engine` 的新檔案。
    

### 步驟三：使用 TensorRT 模型進行推理測試

現在你已經有了 TensorRT 模型，可以用來進行高速推理了。

1. **執行推理指令**：
    
    ```bash
    yolo predict model=yolov8n.engine source=yolo.mp4
    ```
    
    這行指令會使用 `.engine` 模型來處理你的影片，並在終端機中顯示結果。
    

請務必按照上述步驟進行操作，特別是 PyTorch 的安裝部分，這是 PC 和 Jetson Nano 環境之間最大的差異。
