import numpy as np
import math

class ExerciseAnalyzer:
    def __init__(self):
        self.squat_count = 0
        self.is_bottom_position = False
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        point1 = np.array(point1)
        point2 = np.array(point2)
        point3 = np.array(point3)
        
        # Calculate vectors
        vector1 = point1 - point2
        vector2 = point3 - point2
        
        # Calculate angle
        cosine_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        angle = np.arccos(np.clip(cosine_angle, -1, 1))
        
        return np.degrees(angle)
    
    def analyze_squat(self, landmarks):
        """Analyze squat form and provide feedback"""
        if not landmarks:
            return {"error": "No pose detected"}
        
        # Key landmark indices for MediaPipe Pose
        LEFT_HIP = 23
        LEFT_KNEE = 25
        LEFT_ANKLE = 27
        RIGHT_HIP = 24
        RIGHT_KNEE = 26
        RIGHT_ANKLE = 28
        
        # Calculate knee angles
        left_knee_angle = self.calculate_angle(
            landmarks[LEFT_HIP][:2],  # Hip (x,y)
            landmarks[LEFT_KNEE][:2], # Knee (x,y) 
            landmarks[LEFT_ANKLE][:2] # Ankle (x,y)
        )
        
        right_knee_angle = self.calculate_angle(
            landmarks[RIGHT_HIP][:2],
            landmarks[RIGHT_KNEE][:2], 
            landmarks[RIGHT_ANKLE][:2]
        )
        
        # Squat counter logic
        feedback = []
        if left_knee_angle < 90 and right_knee_angle < 90 and not self.is_bottom_position:
            self.squat_count += 1
            self.is_bottom_position = True
            feedback.append("✅ Good squat! Coming up...")
        elif left_knee_angle > 160 and right_knee_angle > 160:
            self.is_bottom_position = False
            feedback.append("🔄 Ready for next squat!")
        
        # Form feedback
        if left_knee_angle > 150:
            feedback.append("⬇️ Go deeper! Bend your knees more")
        elif left_knee_angle < 100:
            feedback.append("🔥 Great depth! Keep chest up")
        
        # Check knee position (prevent knee over toe)
        if landmarks[LEFT_KNEE][0] > landmarks[LEFT_ANKLE][0] + 0.1:
            feedback.append("⚠️ Keep knees behind toes")
        
        return {
            "squat_count": self.squat_count,
            "left_knee_angle": round(left_knee_angle, 1),
            "right_knee_angle": round(right_knee_angle, 1),
            "feedback": feedback,
            "is_exercising": True
        }