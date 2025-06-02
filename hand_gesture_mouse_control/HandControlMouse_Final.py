# Enhanced Hand Mouse Control with Circle Gesture and Pinky Scroll
# Improvements:
# 1. Circle gesture instead of Z gesture (easier to draw)
# 2. Scroll with Index + Pinky finger combination
# 3. Better gesture priority and conflict resolution
# 4. Improved visual feedback and progress indicators

import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import math
import pyautogui
from collections import deque

def detect_circle_gesture(points):
    """Phát hiện cử chỉ vẽ hình tròn - dễ hơn chữ Z (thuật toán cải tiến)"""
    if len(points) < 15:  # Giảm yêu cầu từ 20 xuống 15
        return False
    
    # Chuyển deque thành numpy array để tính toán
    points_array = np.array(list(points))
    
    # Tính tâm của các điểm
    center_x = np.mean(points_array[:, 0])
    center_y = np.mean(points_array[:, 1])
    
    # Tính khoảng cách từ mỗi điểm đến tâm
    distances = []
    for point in points_array:
        dist = math.sqrt((point[0] - center_x)**2 + (point[1] - center_y)**2)
        distances.append(dist)
    
    distances = np.array(distances)
    mean_distance = np.mean(distances)
    std_deviation = np.std(distances)
    
    # Điều kiện dễ hơn: bán kính tối thiểu 25 (thay vì 30) và độ lệch chuẩn 40% (thay vì 30%)
    if mean_distance > 25 and std_deviation < mean_distance * 0.4:
        # Kiểm tra phạm vi góc đơn giản hơn
        angles = []
        for point in points_array:
            angle = math.atan2(point[1] - center_y, point[0] - center_x)
            angles.append(angle)
        
        # Chuyển về degrees
        angles_deg = [math.degrees(angle) % 360 for angle in angles]
        angles_deg.sort()
        
        # Kiểm tra có đủ phạm vi góc không (giảm từ 270 xuống 200 độ)
        angle_coverage = max(angles_deg) - min(angles_deg)
        if angle_coverage > 200:  # Dễ hơn
            return True
            
        # Kiểm tra trường hợp góc bao quanh 0 độ
        if len(angles_deg) > 5:
            # Kiểm tra có góc nào gần 0 và góc nào gần 360
            has_small_angle = any(angle < 60 for angle in angles_deg)
            has_large_angle = any(angle > 300 for angle in angles_deg)
            if has_small_angle and has_large_angle:
                return True
    
    return False

def draw_circle_path(img, points):
    """Vẽ đường đi của cử chỉ vẽ tròn"""
    if len(points) > 1:
        for i in range(1, len(points)):
            cv2.line(img, points[i-1], points[i], (0, 255, 255), 3)
    
    # Hiển thị tâm và bán kính ước tính
    if len(points) > 5:
        points_array = np.array(list(points))
        center_x = int(np.mean(points_array[:, 0]))
        center_y = int(np.mean(points_array[:, 1]))
        cv2.circle(img, (center_x, center_y), 5, (255, 0, 0), -1)
    
    return img

# Cấu hình camera và màn hình
camWidth, camHeight = 640, 480
frameReduction = 100  # Frame reduction 
smoothening = 7

pTime = 0
plocX, plocY = 0, 0  
clocX, clocY = 0, 0  

# Các biến cho chức năng mới
click_cooldown = 0  # Thời gian chờ giữa các lần click
double_click_timer = 0  # Timer cho double click
last_click_time = 0  # Thời gian click cuối
double_click_threshold = 1  # Ngưỡng thời gian cho double click (giây)

# Biến cho gesture hình tròn (thay thế Z)
circle_points = deque(maxlen=30)  # Lưu các điểm để detect hình tròn
circle_gesture_active = False
circle_detection_cooldown = 0

# Biến cho show desktop
show_desktop_cooldown = 0
show_desktop_start_time = 0

# Biến cho scroll với ngón trỏ + ngón út
scroll_start_y = 0
is_scrolling = False
scroll_sensitivity = 5  # Giảm để cuộn nhanh hơn (càng nhỏ càng nhanh)
scroll_cooldown = 0  # Thêm cooldown cho scroll

cap = cv2.VideoCapture(0)
cap.set(3, camWidth)
cap.set(4, camHeight)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()  
print(f"Screen size: {wScr} x {hScr}")
 
while True:
    
    #1. Find Hand Landmarks
    success, img = cap.read()
    if not success:
        continue
        
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    
    #2. get the tip of the index and middle finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]   # Index finger tip
        x2, y2 = lmList[12][1:]  # Middle finger tip
        x5, y5 = lmList[20][1:]  # Pinky tip
        
    #3. Check which fingers are up
    fingers = detector.fingerUp()
    
    # Đảm bảo fingers có đủ phần tử
    if len(fingers) != 5:
        fingers = [0, 0, 0, 0, 0]  # Default: tất cả ngón đều gập
    
    # Vẽ khung hoạt động
    cv2.rectangle(img, (frameReduction, frameReduction), (camWidth - frameReduction, camHeight - frameReduction), (255, 0, 255), 2)
    
    current_time = time.time()
    
    # Tạo thứ tự ưu tiên để tránh xung đột giữa các cử chỉ
    gesture_detected = False
      #4. Scroll với ngón trỏ + ngón út: Index finger + Pinky finger
    if len(lmList) != 0 and fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1 and current_time - scroll_cooldown > 0.05:  # Giảm cooldown để cuộn nhanh hơn
        if not is_scrolling:
            scroll_start_y = y1  # Sử dụng vị trí ngón trỏ làm chuẩn
            is_scrolling = True
            cv2.putText(img, "Scroll Mode - Index+Pinky", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            scroll_distance = y1 - scroll_start_y
            if abs(scroll_distance) > scroll_sensitivity:
                scroll_amount = max(1, int(abs(scroll_distance) / scroll_sensitivity))  # Tối thiểu 1, tối đa tùy khoảng cách
                if scroll_distance > 0:
                    pyautogui.scroll(-scroll_amount * 3)  # Nhân 3 để cuộn nhanh hơn
                    cv2.putText(img, f"Scroll Down ({scroll_amount * 3})", (50, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    pyautogui.scroll(scroll_amount * 3)   # Nhân 3 để cuộn nhanh hơn
                    cv2.putText(img, f"Scroll Up ({scroll_amount * 3})", (50, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                scroll_start_y = y1
                scroll_cooldown = current_time
        
        # Vẽ indicator cho ngón trỏ và ngón út
        cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(img, (x5, y5), 10, (0, 255, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x5, y5), (0, 255, 0), 2)
        gesture_detected = True
        
    else:
        is_scrolling = False
      #5. Circle gesture detection: Chỉ ngón giữa để vẽ tròn
    if not gesture_detected and len(lmList) != 0 and fingers[2] == 1 and sum([fingers[0], fingers[1], fingers[3], fingers[4]]) == 0:
        # Chỉ thêm điểm khi có chuyển động đáng kể
        if len(circle_points) == 0 or (abs(x2 - circle_points[-1][0]) > 2 or abs(y2 - circle_points[-1][1]) > 2):  # Giảm threshold từ 3 xuống 2
            circle_points.append((x2, y2))
        circle_gesture_active = True
        
        # Vẽ đường đi ngay lập tức
        draw_circle_path(img, circle_points)
        cv2.putText(img, f"Drawing Circle... ({len(circle_points)} points)", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Kiểm tra cử chỉ tròn với cooldown giảm
        if len(circle_points) > 15 and current_time - circle_detection_cooldown > 2:  # Giảm cooldown từ 3 xuống 2 giây
            if detect_circle_gesture(circle_points):
                cv2.putText(img, "Circle Gesture - Task View!", (50, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                pyautogui.hotkey('win', 'tab')  # Task View
                circle_points.clear()
                circle_detection_cooldown = current_time
                time.sleep(0.3)  # Giảm sleep từ 0.5 xuống 0.3
        
        gesture_detected = True
        
    else:
        if circle_gesture_active:
            # Kiểm tra circle gesture cuối cùng khi kết thúc - dễ hơn
            if len(circle_points) > 10 and current_time - circle_detection_cooldown > 2:  # Giảm từ 15 xuống 10 điểm
                if detect_circle_gesture(circle_points):
                    cv2.putText(img, "Circle Gesture - Task View!", (50, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    pyautogui.hotkey('win', 'tab')
                    circle_detection_cooldown = current_time
            circle_points.clear()
            circle_gesture_active = False
    
    #6. Show Desktop: All 5 fingers up (cần giữ trong 1.5 giây)
    if not gesture_detected and len(lmList) != 0 and sum(fingers) == 5:
        
        # Nếu là lần đầu phát hiện 5 ngón
        if show_desktop_start_time == 0:
            show_desktop_start_time = current_time
            
        # Kiểm tra đã giữ đủ lâu chưa
        hold_time = current_time - show_desktop_start_time
        required_time = 1.5  # Giữ 1.5 giây
        
        if hold_time >= required_time:
            if current_time - show_desktop_cooldown > 4:  # 4 giây cooldown
                cv2.putText(img, "Show Desktop!", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                pyautogui.hotkey('win', 'd')  # Show Desktop
                show_desktop_cooldown = current_time
                show_desktop_start_time = 0
        else:
            # Hiển thị progress bar
            progress = int((hold_time / required_time) * 100)
            bar_width = 200
            bar_filled = int((hold_time / required_time) * bar_width)
            
            # Vẽ progress bar
            cv2.rectangle(img, (50, 360), (50 + bar_width, 380), (100, 100, 100), 2)
            cv2.rectangle(img, (50, 360), (50 + bar_filled, 380), (0, 255, 0), -1)
            cv2.putText(img, f"Hold 5 fingers... {progress}%", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        gesture_detected = True
        
    else:
        # Reset timer khi không còn 5 ngón
        show_desktop_start_time = 0

    #7. Right click: Thumb and Index finger touch (distance < 40)
    if not gesture_detected and len(lmList) != 0 and fingers[0] == 1 and fingers[1] == 1:
        # Tính khoảng cách giữa ngón cái và ngón trỏ
        thumb_index_distance, img, lineInfo = detector.findDistance(4, 8, img)
        if thumb_index_distance < 40:
            cv2.putText(img, "Right Click", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (255, 0, 0), cv2.FILLED)
            pyautogui.rightClick()
            time.sleep(0.3)  # Tránh click liên tục
            gesture_detected = True

    #8. Both index and middle finger are up : Clicking mode
    if not gesture_detected and len(lmList) != 0 and fingers[1] == 1 and fingers[2] == 1:
        length, img, lineInfo = detector.findDistance(8, 12, img)
        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
            
            # Kiểm tra double click
            if current_time - last_click_time < double_click_threshold:
                pyautogui.doubleClick()
                cv2.putText(img, "Double Click!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            else:
                autopy.mouse.click()
                cv2.putText(img, "Click!", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            last_click_time = current_time
            time.sleep(0.1)  # Tránh click liên tục
            gesture_detected = True
    
    #9. Only index finger : Moving mode (ưu tiên thấp nhất)
    if not gesture_detected and len(lmList) != 0 and fingers[1] == 1 and fingers[2] == 0:

        #10. Convert Coordinates
        x3 = np.interp(x1, (frameReduction, camWidth-frameReduction), (0, wScr))
        y3 = np.interp(y1, (frameReduction, camHeight-frameReduction), (0, hScr))
        
        #11. Smoothen Values
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening
        
        #12. Move Mouse
        autopy.mouse.move(wScr-clocX, clocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        plocX, plocY = clocX, clocY

    # Vẽ đường đi circle gesture nếu đang active
    if circle_gesture_active and len(circle_points) > 1:
        draw_circle_path(img, circle_points)

    #13. Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
      # Hiển thị hướng dẫn cải tiến
    instructions = [
        "1 finger: Move mouse",
        "2 fingers close: Click/Double-click", 
        "Thumb+Index close: Right-click",
        "Index+Pinky up/down: Scroll (FAST)",
        "Only Middle finger: Draw circle for Task View",
        "Hold 5 fingers 1.5s: Show Desktop"
    ]
    
    for i, instruction in enumerate(instructions):
        y_pos = 400 + i * 20
        cv2.putText(img, instruction, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    #14. Display
    cv2.imshow("Enhanced Hand Mouse Control - Circle + Pinky Scroll", img)
    
    # Thoát khi nhấn 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Program ended successfully!")
