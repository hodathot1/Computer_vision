# Điều Khiển Chuột Máy Tính Bằng Cử Chỉ Tay

## 1. Tổng Quan
Dự án này phát triển một hệ thống điều khiển chuột máy tính thông qua cử chỉ tay, sử dụng camera để nhận diện và xử lý các cử chỉ tay, sau đó ánh xạ chúng thành các thao tác chuột tương ứng trên máy tính.

## 2. Công Nghệ Sử Dụng
- **Python**: Ngôn ngữ lập trình chính
- **OpenCV**: Xử lý hình ảnh và video
- **MediaPipe**: Framework nhận diện bàn tay
- **AutoPy**: Điều khiển chuột và bàn phím
- **PyAutoGUI**: Hỗ trợ các thao tác nâng cao với chuột và bàn phím

## 3. Cấu Trúc Dự Án

### 3.1. HandTrackingModule.py
Module xử lý nhận diện bàn tay sử dụng MediaPipe.

#### Các Class và Hàm Chính:
```python
class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5)
    def findHands(self, img, draw=True)
    def findPosition(self, img, handNo=0, draw=True)
    def fingerUp(self)
    def findDistance(self, p1, p2, img=None, draw=True, r=15, t=3)
```

#### Các Biến Quan Trọng:
- `mode`: Chế độ xử lý ảnh (tĩnh/động)
- `maxHands`: Số lượng bàn tay tối đa có thể nhận diện
- `detectionCon`: Ngưỡng tin cậy cho việc phát hiện
- `trackCon`: Ngưỡng tin cậy cho việc theo dõi
- `tipIds`: ID của các đầu ngón tay [4, 8, 12, 16, 20]

### 3.2. HandControlMouse_Final.py
File chính chứa logic điều khiển chuột.

#### Các Biến Cấu Hình:
```python
# Cấu hình camera
camWidth, camHeight = 640, 480
frameReduction = 100
smoothening = 7

# Biến theo dõi vị trí
plocX, plocY = 0, 0  # Vị trí trước
clocX, clocY = 0, 0  # Vị trí hiện tại
```

## 4. Các Cử Chỉ Được Hỗ Trợ

### 4.1. Di Chuyển Chuột
- **Cử chỉ**: Chỉ ngón trỏ giơ lên
- **Xử lý**: 
  ```python
  if fingers[1] == 1 and fingers[2] == 0:
      x3 = np.interp(x1, (frameReduction, camWidth-frameReduction), (0, wScr))
      y3 = np.interp(y1, (frameReduction, camHeight-frameReduction), (0, hScr))
  ```

### 4.2. Click Chuột
- **Cử chỉ**: Ngón trỏ và ngón giữa giơ lên
- **Điều kiện**: Khoảng cách giữa hai ngón < 40
- **Xử lý**: `autopy.mouse.click()`

### 4.3. Double Click
- **Cử chỉ**: Giống click chuột
- **Điều kiện**: Thời gian giữa hai click < 1 giây
- **Xử lý**: `pyautogui.doubleClick()`

### 4.4. Right Click
- **Cử chỉ**: Ngón cái và ngón trỏ chạm nhau
- **Xử lý**: `pyautogui.rightClick()`

### 4.5. Cuộn Màn Hình
- **Cử chỉ**: Ngón trỏ và ngón út giơ lên
- **Xử lý**: 
  ```python
  scroll_distance = y1 - scroll_start_y
  pyautogui.scroll(-scroll_amount * 3)  # Cuộn xuống
  pyautogui.scroll(scroll_amount * 3)   # Cuộn lên
  ```

### 4.6. Cử Chỉ Hình Tròn
- **Cử chỉ**: Chỉ ngón giữa giơ lên và vẽ hình tròn
- **Xử lý**: 
  ```python
  if detect_circle_gesture(circle_points):
      pyautogui.hotkey('win', 'tab')  # Mở Task View
  ```

### 4.7. Show Desktop
- **Cử chỉ**: Giữ 5 ngón tay giơ lên trong 1.5 giây
- **Xử lý**: `pyautogui.hotkey('win', 'd')`

## 5. Cải Tiến và Tối Ưu

### 5.1. Làm Mượt Chuyển Động
```python
clocX = plocX + (x3 - plocX) / smoothening
clocY = plocY + (y3 - plocY) / smoothening
```

### 5.2. Xử Lý Xung Đột
- Sử dụng biến `gesture_detected` để tránh xung đột giữa các cử chỉ
- Thứ tự ưu tiên: Scroll > Circle > Show Desktop > Right Click > Click > Move

### 5.3. Cooldown và Delay
- `click_cooldown`: Tránh click liên tục
- `double_click_timer`: Kiểm soát double click
- `scroll_cooldown`: Điều chỉnh tốc độ cuộn
- `circle_detection_cooldown`: Tránh phát hiện hình tròn liên tục

## 6. Hướng Dẫn Sử Dụng

1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install opencv-python
   pip install mediapipe
   pip install autopy
   pip install pyautogui
   ```

2. Chạy chương trình:
   ```bash
   python HandControlMouse_Final.py
   ```

3. Các cử chỉ cơ bản:
   - 1 ngón trỏ: Di chuyển chuột
   - 2 ngón (trỏ + giữa): Click/Double-click
   - Ngón cái + trỏ: Right-click
   - Ngón trỏ + út: Cuộn màn hình
   - Chỉ ngón giữa: Vẽ tròn để mở Task View
   - Giữ 5 ngón 1.5s: Hiện Desktop

## 7. Kết Luận
Dự án đã phát triển thành công một hệ thống điều khiển chuột bằng cử chỉ tay với nhiều tính năng hữu ích. Hệ thống có khả năng nhận diện chính xác các cử chỉ và ánh xạ chúng thành các thao tác chuột tương ứng, mang lại trải nghiệm người dùng tốt và tiện lợi. 

## 8. Chi Tiết Kỹ Thuật và Các Phép Tính Toán

### 8.1. Xử Lý Thời Gian
```python
# Biến thời gian
pTime = 0  # Previous Time - Thời điểm trước đó
cTime = 0  # Current Time - Thời điểm hiện tại
fps = 1 / (cTime - pTime)  # Frames Per Second - Số khung hình trên giây
```

#### Giải thích:
- `pTime`: Lưu thời điểm của frame trước đó
- `cTime`: Lưu thời điểm của frame hiện tại
- `fps`: Được tính bằng cách lấy nghịch đảo của khoảng thời gian giữa hai frame
- Công thức: fps = 1 / (thời điểm hiện tại - thời điểm trước đó)

### 8.2. Chuyển Đổi Tọa Độ
```python
# Chuyển đổi tọa độ từ camera sang màn hình
x3 = np.interp(x1, (frameReduction, camWidth-frameReduction), (0, wScr))
y3 = np.interp(y1, (frameReduction, camHeight-frameReduction), (0, hScr))
```

#### Giải thích:
- `np.interp`: Hàm nội suy tuyến tính của NumPy
- Công thức: output = start2 + (value - start1) * (end2 - start2) / (end1 - start1)
- Trong đó:
  - `start1, end1`: Khoảng giá trị đầu vào (từ camera)
  - `start2, end2`: Khoảng giá trị đầu ra (màn hình)
  - `value`: Giá trị cần chuyển đổi

### 8.3. Làm Mượt Chuyển Động
```python
# Làm mượt chuyển động chuột
clocX = plocX + (x3 - plocX) / smoothening
clocY = plocY + (y3 - plocY) / smoothening
```

#### Giải thích:
- `smoothening`: Hệ số làm mượt (giá trị càng lớn, chuyển động càng mượt)
- Công thức: vị trí mới = vị trí cũ + (vị trí mục tiêu - vị trí cũ) / hệ số mượt
- Mục đích: Giảm độ giật của chuột khi di chuyển

### 8.4. Phát Hiện Hình Tròn
```python
def detect_circle_gesture(points):
    # Tính tâm hình tròn
    center_x = np.mean(points_array[:, 0])
    center_y = np.mean(points_array[:, 1])
    
    # Tính khoảng cách từ các điểm đến tâm
    distances = []
    for point in points_array:
        dist = math.sqrt((point[0] - center_x)**2 + (point[1] - center_y)**2)
        distances.append(dist)
    
    # Kiểm tra độ lệch chuẩn
    mean_distance = np.mean(distances)
    std_deviation = np.std(distances)
```

#### Giải thích:
- Sử dụng phương pháp thống kê để xác định hình tròn
- Các bước:
  1. Tính tâm hình tròn bằng trung bình cộng các điểm
  2. Tính khoảng cách từ mỗi điểm đến tâm
  3. Tính độ lệch chuẩn của các khoảng cách
  4. Nếu độ lệch chuẩn nhỏ, các điểm tạo thành hình tròn

### 8.5. Xử Lý Cooldown
```python
# Các biến cooldown
click_cooldown = 0
double_click_timer = 0
scroll_cooldown = 0
circle_detection_cooldown = 0

# Kiểm tra cooldown
if current_time - click_cooldown > 0.3:  # 300ms
    # Thực hiện hành động
    click_cooldown = current_time
```

#### Giải thích:
- Cooldown: Thời gian chờ giữa các hành động
- Mục đích:
  - Tránh thực hiện hành động quá nhanh
  - Tạo độ trễ tự nhiên giữa các thao tác
  - Ngăn chặn việc kích hoạt nhiều lần không mong muốn

### 8.6. Tính Toán Khoảng Cách
```python
def findDistance(p1, p2, img=None, draw=True, r=15, t=3):
    x1, y1 = self.lmList[p1][1:]
    x2, y2 = self.lmList[p2][1:]
    length = math.hypot(x2 - x1, y2 - y1)
```

#### Giải thích:
- Sử dụng định lý Pythagoras để tính khoảng cách
- Công thức: d = √((x2-x1)² + (y2-y1)²)
- Ứng dụng: Xác định khoảng cách giữa các ngón tay để phát hiện cử chỉ

## 9. Kết Luận
Dự án đã phát triển thành công một hệ thống điều khiển chuột bằng cử chỉ tay với nhiều tính năng hữu ích. Hệ thống có khả năng nhận diện chính xác các cử chỉ và ánh xạ chúng thành các thao tác chuột tương ứng, mang lại trải nghiệm người dùng tốt và tiện lợi. 