import cv2
import numpy as np
from hand_detector import HandDetector
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

# Initialize the camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

# Initialize hand detector
detector = HandDetector(detection_confidence=0.7)

# Initialize audio device
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volume_range = volume.GetVolumeRange()
min_vol, max_vol = volume_range[0], volume_range[1]

while True:
    success, img = cap.read()
    
    # Find hands
    img = detector.find_hands(img)
    landmark_list = detector.find_position(img)
    
    if len(landmark_list) != 0:
        # Get the coordinates of thumb and index finger
        thumb_x, thumb_y = landmark_list[4][1], landmark_list[4][2]
        index_x, index_y = landmark_list[8][1], landmark_list[8][2]
        
        # Calculate center point
        center_x, center_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
        
        # Draw circles on the points and line between them
        cv2.circle(img, (thumb_x, thumb_y), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (index_x, index_y), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 255), 3)
        cv2.circle(img, (center_x, center_y), 15, (255, 0, 255), cv2.FILLED)
        
        # Calculate length between points
        length = math.hypot(index_x - thumb_x, index_y - thumb_y)
        
        # Convert length range (50-300) to volume range (-65.25-0)
        vol = np.interp(length, [50, 300], [min_vol, max_vol])
        
        # Set system volume
        volume.SetMasterVolumeLevel(vol, None)
        
        # Draw volume bar
        vol_bar = np.interp(length, [50, 300], [400, 150])
        vol_percentage = np.interp(length, [50, 300], [0, 100])
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(vol_percentage)}%', (40, 450), 
                    cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    # Display FPS
    cv2.putText(img, "Hand Gesture Volume Control", (10, 70), 
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    
    # Show image
    cv2.imshow("Image", img)
    
    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()