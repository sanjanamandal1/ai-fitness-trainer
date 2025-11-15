import mediapipe as mp
import cv2
import numpy as np

print("🧪 Testing MediaPipe installation...")

try:
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    print("✅ MediaPipe Pose - OK")
    
    # Test OpenCV
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite('test.jpg', test_image)
    print("✅ OpenCV - OK")
    
    print("🎉 All AI packages working! Ready for pose detection.")
    
except Exception as e:
    print(f"❌ Error: {e}")