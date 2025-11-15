import cv2

print("🔍 Testing webcam access...")

# Try different camera IDs
for camera_id in [0, 1, 2]:
    cap = cv2.VideoCapture(camera_id)
    
    if cap.isOpened():
        print(f"✅ Camera FOUND at ID: {camera_id}")
        
        # Try to read a frame
        ret, frame = cap.read()
        if ret:
            print(f"   📸 Can capture frames - Resolution: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print("   ❌ Can open but cannot read frames")
            
        cap.release()
        break
else:
    print("❌ No cameras found. Check permissions.")