# GIẢI THÍCH CHI TIẾT CODE ĐIỀU KHIỂN CHUỘT BẰNG TAY

## TỔNG QUAN DỰ ÁN

Dự án này tạo ra một hệ thống điều khiển chuột máy tính bằng cử chỉ tay sử dụng computer vision. Hệ thống gồm 2 file chính:
- **HandTrackingModule.py**: Module phát hiện và theo dõi bàn tay
- **HandControlMouse_Final.py**: Ứng dụng chính điều khiển chuột

---

## 1. FILE HANDTRACKINGMODULE.PY

### Mục đích
Module này tạo ra class `handDetector` để phát hiện và theo dõi bàn tay sử dụng thư viện MediaPipe của Google.

### Các thư viện sử dụng
```python
import cv2              # OpenCV - Xử lý hình ảnh và video
import mediapipe as mp  # MediaPipe - Thư viện AI của Google cho hand tracking
import numpy as np      # NumPy - Tính toán mảng và ma trận
import time             # Time - Đo thời gian và FPS
import math             # Math - Các phép tính toán học
```

### Class handDetector

#### Hàm khởi tạo __init__()
```python
def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
```
**Các tham số:**
- `mode`: 
  - False = video streaming mode (liên tục)
  - True = static image mode (ảnh tĩnh)
- `maxHands`: Số lượng bàn tay tối đa có thể phát hiện (mặc định 2)
- `detectionCon`: Độ tin cậy tối thiểu để phát hiện bàn tay (0.5 = 50%)
- `trackCon`: Độ tin cậy tối thiểu để theo dõi bàn tay (0.5 = 50%)

**Các biến quan trọng:**
- `self.tipIds = [4, 8, 12, 16, 20]`: ID của các đầu ngón tay
  - 4: Ngón cái (thumb)
  - 8: Ngón trỏ (index)
  - 12: Ngón giữa (middle)
  - 16: Ngón áp út (ring)
  - 20: Ngón út (pinky)

#### Hàm findHands()
```python
def findHands(self, img, draw=True):
```
**Chức năng:**
- Chuyển đổi ảnh từ BGR (Blue-Green-Red) sang RGB (Red-Green-Blue)
- Sử dụng MediaPipe để phát hiện bàn tay trong ảnh
- Vẽ các điểm landmark (21 điểm) và kết nối giữa chúng nếu draw=True

**Trả về:** Ảnh đã được vẽ các điểm landmark

#### Hàm findPosition()
```python
def findPosition(self, img, handNo=0, draw=True):
```
**Chức năng:**
- Lấy tọa độ của 21 điểm landmark trên bàn tay
- Mỗi điểm có định dạng [id, x, y]
- Tính toán bounding box (hộp bao quanh bàn tay)

**Tham số:**
- `handNo`: Chỉ số bàn tay (0 = bàn tay đầu tiên)
- `draw`: Có vẽ các điểm và bounding box không

**Trả về:** (lmList, bbox)
- `lmList`: Danh sách 21 điểm landmark
- `bbox`: Tọa độ bounding box (xmin, ymin, xmax, ymax)

#### Hàm fingerUp()
```python
def fingerUp(self):
```
**Chức năng:** Kiểm tra ngón tay nào đang giơ lên

**Cách hoạt động:**
- **Ngón cái (thumb)**: So sánh tọa độ x của đầu ngón cái với khớp gần đó
  ```python
  if self.lmList[4][1] > self.lmList[3][1]:  # Ngón cái giơ lên
  ```
- **Các ngón khác**: So sánh tọa độ y của đầu ngón với khớp cách 2 vị trí
  ```python
  if self.lmList[8][2] < self.lmList[6][2]:  # Ngón trỏ giơ lên
  ```

**Trả về:** List [thumb, index, middle, ring, pinky] với 1=giơ lên, 0=gập xuống

#### Hàm findDistance()
```python
def findDistance(self, p1, p2, img=None, draw=True, r=15, t=3):
```
**Chức năng:** Tính khoảng cách giữa 2 điểm landmark

**Tham số:**
- `p1, p2`: ID của 2 điểm landmark
- `r`: Bán kính vòng tròn vẽ tại các điểm
- `t`: Độ dày đường thẳng

**Trả về:** (length, img, [x1, y1, x2, y2, cx, cy])
- `length`: Khoảng cách Euclidean
- `cx, cy`: Tọa độ điểm giữa

#### Các hàm hỗ trợ khác
- `countFingers()`: Đếm số ngón tay giơ lên
- `getHandCenter()`: Lấy tọa độ tâm bàn tay (điểm landmark số 9)
- `getFingerTip()`: Lấy tọa độ đầu ngón tay theo ID

---

## 2. FILE HANDCONTROLMOUSE_FINAL.PY

### Các thư viện sử dụng
```python
import cv2                      # Xử lý video
import numpy as np              # Tính toán mảng
import HandTrackingModule as htm # Module tự tạo
import time                     # Thời gian
import autopy                   # Điều khiển chuột (thư viện cũ)
import math                     # Toán học
import pyautogui                # Điều khiển bàn phím/chuột (thư viện mới)
from collections import deque   # Queue có giới hạn kích thước
```

### Các hàm chính

#### Hàm detect_circle_gesture()
```python
def detect_circle_gesture(points):
```
**Mục đích:** Phát hiện cử chỉ vẽ hình tròn

**Thuật toán:**
1. **Kiểm tra số điểm:** Cần ít nhất 15 điểm
2. **Tính tâm:** `center_x = np.mean(points[:, 0])`
3. **Tính khoảng cách:** Từ các điểm đến tâm
4. **Kiểm tra độ đều:** `std_deviation < mean_distance * 0.4`
5. **Kiểm tra góc bao phủ:** Phải > 200 độ để tạo thành vòng tròn

**Điều kiện để là hình tròn:**
- Khoảng cách trung bình > 25 pixel
- Độ lệch chuẩn nhỏ (tạo hình tròn đều)
- Bao phủ góc lớn (> 200°) hoặc có góc nhỏ và góc lớn

#### Hàm draw_circle_path()
```python
def draw_circle_path(img, points):
```
**Chức năng:**
- Vẽ đường nối các điểm đã thu thập (màu cyan)
- Vẽ điểm tâm của hình tròn (màu xanh dương)

### Các biến cấu hình

#### Thiết lập camera và màn hình
```python
camWidth, camHeight = 640, 480    # Kích thước camera
frameReduction = 100              # Vùng biên không sử dụng (tránh edge detection)
smoothening = 7                   # Độ mượt của con trỏ chuột (càng cao càng mượt)
wScr, hScr = autopy.screen.size() # Kích thước màn hình thực
```

#### Biến theo dõi vị trí chuột
```python
pTime = 0                    # Thời gian frame trước (cho tính FPS)
plocX, plocY = 0, 0         # Vị trí chuột frame trước
clocX, clocY = 0, 0         # Vị trí chuột frame hiện tại
```

#### Biến điều khiển click
```python
click_cooldown = 0           # Thời gian chờ giữa các lần click
last_click_time = 0          # Thời gian click cuối cùng
double_click_threshold = 1   # Ngưỡng thời gian cho double click (1 giây)
```

#### Biến cử chỉ vẽ tròn
```python
circle_points = deque(maxlen=30)  # Queue lưu tối đa 30 điểm gần nhất
circle_gesture_active = False     # Trạng thái đang vẽ tròn
circle_detection_cooldown = 0     # Thời gian chờ giữa các lần phát hiện (tránh spam)
```

#### Biến show desktop
```python
show_desktop_cooldown = 0      # Thời gian chờ giữa các lần show desktop
show_desktop_start_time = 0    # Thời điểm bắt đầu giữ 5 ngón tay
```

#### Biến cuộn trang
```python
scroll_start_y = 0           # Vị trí Y bắt đầu cuộn
is_scrolling = False         # Trạng thái đang cuộn
scroll_sensitivity = 1       # Độ nhạy cuộn (pixel di chuyển)
scroll_cooldown = 0          # Thời gian chờ giữa các lần cuộn
```

### Vòng lặp chính - Các cử chỉ

#### 1. Thu thập dữ liệu bàn tay
```python
img = detector.findHands(img)           # Phát hiện bàn tay
lmList, bbox = detector.findPosition(img)  # Lấy tọa độ 21 điểm landmark
fingers = detector.fingerUp()           # Kiểm tra ngón tay nào giơ lên

# Lấy tọa độ các ngón tay quan trọng:
x1, y1 = lmList[8][1:]   # Ngón trỏ (landmark index 8)
x2, y2 = lmList[12][1:]  # Ngón giữa (landmark index 12)  
x5, y5 = lmList[20][1:]  # Ngón út (landmark index 20)
```

#### 2. Cử chỉ cuộn trang (Index + Pinky)
**Điều kiện kích hoạt:**
```python
fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1
```
- Chỉ ngón trỏ và ngón út giơ lên
- Các ngón khác gập xuống

**Cách hoạt động:**
1. Lưu vị trí Y ban đầu của ngón trỏ
2. Tính khoảng cách di chuyển theo trục Y
3. Nếu di chuyển > sensitivity → cuộn
4. `pyautogui.scroll(-amount)` để cuộn xuống
5. `pyautogui.scroll(amount)` để cuộn lên

**Hiệu ứng trực quan:**
- Vẽ vòng tròn xanh tại ngón trỏ và ngón út
- Vẽ đường thẳng nối 2 ngón tay
- Hiển thị text "Scroll Mode"

#### 3. Cử chỉ vẽ tròn (Chỉ ngón giữa)
**Điều kiện kích hoạt:**
```python
fingers[2] == 1 and sum([fingers[0], fingers[1], fingers[3], fingers[4]]) == 0
```
- Chỉ ngón giữa giơ lên
- Tất cả các ngón khác gập xuống

**Cách hoạt động:**
1. Thu thập tọa độ ngón giữa vào `circle_points`
2. Vẽ đường path theo chuyển động
3. Khi có đủ điểm (>15), gọi `detect_circle_gesture()`
4. Nếu phát hiện hình tròn → `pyautogui.hotkey('win', 'tab')` (Task View)

**Tối ưu hóa:**
- Chỉ thêm điểm mới nếu di chuyển > 2 pixel (tránh nhiễu)
- Cooldown 2 giây giữa các lần phát hiện

#### 4. Show Desktop (5 ngón tay)
**Điều kiện kích hoạt:**
```python
sum(fingers) == 5
```
- Tất cả 5 ngón tay giơ lên

**Cách hoạt động:**
1. Phải giữ trong 1 giây liên tục
2. Hiển thị progress bar theo thời gian
3. Khi đủ thời gian → `pyautogui.hotkey('win', 'd')` (Show Desktop)
4. Cooldown 4 giây giữa các lần kích hoạt

**Progress Bar:**
```python
progress = int((hold_time / required_time) * 100)
bar_filled = int((hold_time / required_time) * bar_width)
cv2.rectangle(img, (50, 360), (50 + bar_filled, 380), (0, 255, 0), -1)
```

#### 5. Right Click (Ngón cái + Ngón trỏ chạm nhau)
**Điều kiện kích hoạt:**
```python
fingers[0] == 1 and fingers[1] == 1 and distance < 40
```
- Ngón cái và ngón trỏ giơ lên
- Khoảng cách giữa chúng < 40 pixel

**Cách hoạt động:**
1. Tính khoảng cách bằng `detector.findDistance(4, 8, img)`
2. Nếu khoảng cách đủ gần → `pyautogui.rightClick()`
3. Hiển thị vòng tròn đỏ tại điểm giữa 2 ngón tay

#### 6. Click/Double Click (Ngón trỏ + Ngón giữa)
**Điều kiện kích hoạt:**
```python
fingers[1] == 1 and fingers[2] == 1 and distance < 40
```
- Ngón trỏ và ngón giữa giơ lên
- Khoảng cách giữa chúng < 40 pixel

**Logic Double Click:**
```python
if current_time - last_click_time < double_click_threshold:
    pyautogui.doubleClick()  # Double click nếu click trong vòng 1 giây
else:
    autopy.mouse.click()     # Single click
```

#### 7. Di chuyển chuột (Chỉ ngón trỏ)
**Điều kiện kích hoạt:**
```python
fingers[1] == 1 and fingers[2] == 0
```
- Chỉ ngón trỏ giơ lên (ưu tiên thấp nhất)

**Quy trình chuyển đổi tọa độ:**
1. **Camera → Screen mapping:**
   ```python
   x3 = np.interp(x1, (frameReduction, camWidth-frameReduction), (0, wScr))
   y3 = np.interp(y1, (frameReduction, camHeight-frameReduction), (0, hScr))
   ```

2. **Làm mượt chuyển động:**
   ```python
   clocX = plocX + (x3 - plocX) / smoothening
   clocY = plocY + (y3 - plocY) / smoothening
   ```

3. **Di chuyển chuột:**
   ```python
   autopy.mouse.move(wScr-clocX, clocY)  # Đảo ngược X để mirror
   ```

### Cơ chế ưu tiên cử chỉ

Code sử dụng biến `gesture_detected` để đảm bảo chỉ một cử chỉ được thực hiện trong mỗi frame:

**Thứ tự ưu tiên (cao → thấp):**
1. Cuộn trang (Index + Pinky) - **Cao nhất**
2. Vẽ tròn (Chỉ Middle)
3. Show desktop (5 ngón tay)
4. Right click (Thumb + Index chạm)
5. Click/Double click (Index + Middle chạm)
6. Di chuyển chuột (Chỉ Index) - **Thấp nhất**

### Tối ưu hóa hiệu suất

#### Cooldown Timers
- **Scroll**: 0.05 giây - Tránh cuộn quá nhanh
- **Circle**: 2 giây - Tránh spam Task View
- **Show Desktop**: 4 giây - Tránh kích hoạt liên tục
- **Click**: 0.1-0.3 giây - Tránh click nhiều lần

#### Smoothening
```python
smoothening = 7  # Càng cao càng mượt, nhưng càng chậm phản hồi
```

#### Frame Reduction
```python
frameReduction = 100  # Tạo vùng buffer 100px từ mép màn hình
```
- Tránh false detection ở biên camera
- Tạo vùng hoạt động ổn định ở giữa

#### FPS Monitoring
```python
fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
cv2.putText(img, f"FPS: {int(fps)}", (20, 50), ...)
```

### Xử lý lỗi và Edge Cases

1. **Kiểm tra landmark hợp lệ:**
   ```python
   if len(lmList) != 0:  # Đảm bảo có phát hiện bàn tay
   ```

2. **Kiểm tra fingers array:**
   ```python
   if len(fingers) != 5:
       fingers = [0, 0, 0, 0, 0]  # Reset nếu lỗi
   ```

3. **Tránh chia cho 0:**
   ```python
   fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
   ```

### Kết thúc chương trình
```python
if cv2.waitKey(1) & 0xFF == ord('q'):  # Nhấn 'q' để thoát
    break

cap.release()           # Giải phóng camera
cv2.destroyAllWindows() # Đóng tất cả cửa sổ OpenCV
```

---

## TỔNG KẾT

Đây là một hệ thống điều khiển chuột hoàn chỉnh sử dụng computer vision, cho phép người dùng:
- **Di chuyển chuột** bằng ngón trỏ
- **Click/Double click** bằng cách chạm ngón trỏ và ngón giữa  
- **Right click** bằng cách chạm ngón cái và ngón trỏ
- **Cuộn trang** bằng ngón trỏ và ngón út
- **Mở Task View** bằng cách vẽ hình tròn
- **Show Desktop** bằng cách giơ 5 ngón tay

Hệ thống được thiết kế với độ ổn định cao, tránh false positive và có trải nghiệm người dùng mượt mà.
