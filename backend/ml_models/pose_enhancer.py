import numpy as np
import math

class EnhancedPoseDetector:
    def __init__(self):
        self.pose_landmarks = None
        self.previous_landmarks = None
        
    def simulate_pose_landmarks(self, frame_shape=(480, 640)):
        """Simulate realistic pose landmarks for development"""
        # Simulate a person in different positions
        positions = [
            # Standing position
            {
                'left_knee': 170, 'right_knee': 172, 
                'left_elbow': 165, 'right_elbow': 167,
                'left_hip': 150, 'right_hip': 152,
                'state': 'standing'
            },
            # Half squat position
            {
                'left_knee': 120, 'right_knee': 122,
                'left_elbow': 160, 'right_elbow': 162,
                'left_hip': 130, 'right_hip': 132,
                'state': 'half_squat'
            },
            # Full squat position
            {
                'left_knee': 85, 'right_knee': 87,
                'left_elbow': 155, 'right_elbow': 157,
                'left_hip': 100, 'right_hip': 102,
                'state': 'full_squat'
            },
            # Push-up position
            {
                'left_knee': 175, 'right_knee': 175,
                'left_elbow': 75, 'right_elbow': 77,
                'left_hip': 170, 'right_hip': 172,
                'state': 'pushup_bottom'
            }
        ]
        
        # Cycle through positions for realistic simulation
        import time
        position_index = int(time.time() * 0.5) % len(positions)
        current_pos = positions[position_index]
        
        # Add some random variation
        variation = np.random.normal(0, 3, 6)  # Small random variations
        angles = {
            'left_knee': max(60, min(180, current_pos['left_knee'] + variation[0])),
            'right_knee': max(60, min(180, current_pos['right_knee'] + variation[1])),
            'left_elbow': max(30, min(180, current_pos['left_elbow'] + variation[2])),
            'right_elbow': max(30, min(180, current_pos['right_elbow'] + variation[3])),
            'left_hip': max(80, min(180, current_pos['left_hip'] + variation[4])),
            'right_hip': max(80, min(180, current_pos['right_hip'] + variation[5]))
        }
        
        return angles, current_pos['state']
    
    def calculate_advanced_angles(self):
        """Calculate detailed joint angles for better form analysis"""
        angles, state = self.simulate_pose_landmarks()
        return angles
    
    def detect_exercise_phase(self, angles, exercise_type):
        """Detect which phase of exercise user is in"""
        if exercise_type == "squats":
            knee_angle = (angles['left_knee'] + angles['right_knee']) / 2
            if knee_angle < 90:
                return "bottom_position"
            elif knee_angle > 160:
                return "top_position"
            else:
                return "transition"
                
        elif exercise_type == "pushups":
            elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2
            if elbow_angle < 90:
                return "bottom_position"
            elif elbow_angle > 160:
                return "top_position"
            else:
                return "transition"
        
        return "unknown"
    
    def analyze_body_symmetry(self, angles):
        """Analyze left-right symmetry in movement"""
        knee_diff = abs(angles['left_knee'] - angles['right_knee'])
        elbow_diff = abs(angles['left_elbow'] - angles['right_elbow'])
        hip_diff = abs(angles['left_hip'] - angles['right_hip'])
        
        symmetry_score = 100 - (knee_diff + elbow_diff + hip_diff) / 3
        
        feedback = []
        if knee_diff > 15:
            feedback.append("⚖️ Knee asymmetry detected")
        if elbow_diff > 20:
            feedback.append("⚖️ Arm asymmetry detected")
        if hip_diff > 10:
            feedback.append("⚖️ Hip asymmetry detected")
            
        return {
            "symmetry_score": max(0, symmetry_score),
            "feedback": feedback,
            "differences": {
                "knees": knee_diff,
                "elbows": elbow_diff,
                "hips": hip_diff
            }
        }