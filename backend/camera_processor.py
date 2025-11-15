import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import base64

class RealCameraProcessor:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.latest_analysis = {}
        self.camera_available = False
        
        # MediaPipe setup
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def start_camera(self, camera_id=0):
        """Force real camera usage"""
        try:
            print(f"🎥 Attempting to start REAL camera at ID: {camera_id}")
            
            # Release any existing camera
            if self.camera:
                self.camera.release()
                
            self.camera = cv2.VideoCapture(camera_id)
            
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.camera.isOpened():
                print("❌ Primary camera failed, trying alternatives...")
                # Try other camera IDs
                for alt_id in [1, 2, 3]:
                    self.camera = cv2.VideoCapture(alt_id)
                    if self.camera.isOpened():
                        camera_id = alt_id
                        print(f"✅ Using alternate camera ID: {camera_id}")
                        break
            
            if self.camera.isOpened():
                self.camera_available = True
                self.is_running = True
                
                # Test frame capture
                ret, test_frame = self.camera.read()
                if ret:
                    print(f"✅ REAL CAMERA WORKING! Frame size: {test_frame.shape}")
                    
                    # Start camera thread
                    self.camera_thread = threading.Thread(target=self._camera_loop)
                    self.camera_thread.daemon = True
                    self.camera_thread.start()
                    
                    return {
                        "message": "✅ REAL Camera started successfully!", 
                        "camera_id": camera_id,
                        "mode": "real_camera",
                        "frame_size": f"{test_frame.shape[1]}x{test_frame.shape[0]}"
                    }
                else:
                    self.camera_available = False
                    return {"error": "Camera opened but cannot read frames"}
            else:
                self.camera_available = False
                return {"error": "No camera could be opened"}
                
        except Exception as e:
            print(f"❌ Camera error: {e}")
            self.camera_available = False
            return {"error": f"Camera initialization failed: {str(e)}"}
    
    def _camera_loop(self):
        """Real camera processing loop"""
        frame_count = 0
        while self.is_running and self.camera_available:
            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame
                frame_count += 1
                
                # Analyze every 3rd frame for performance
                if frame_count % 3 == 0:
                    self._analyze_frame(frame)
                    
            time.sleep(0.033)  # ~30 FPS
    
    def _analyze_frame(self, frame):
        """Analyze pose in real camera frame"""
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Extract landmarks
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x, 'y': landmark.y, 'z': landmark.z,
                        'visibility': landmark.visibility
                    })
                
                # Real analysis
                analysis = self._real_pose_analysis(landmarks)
                analysis["mode"] = "real_camera"
                analysis["person_detected"] = True
                self.latest_analysis = analysis
                
                # Draw pose landmarks on frame (for visualization)
                self.mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )
                
            else:
                self.latest_analysis = {
                    "pose_detected": False, 
                    "message": "⏳ Waiting for person... Stand in camera view",
                    "mode": "real_camera",
                    "person_detected": False
                }
                
        except Exception as e:
            self.latest_analysis = {
                "error": f"Analysis error: {str(e)}",
                "mode": "real_camera"
            }
    
    def _real_pose_analysis(self, landmarks):
        """Real pose analysis using camera data"""
        try:
            # MediaPipe landmark indices
            LEFT_SHOULDER = 11; LEFT_ELBOW = 13; LEFT_WRIST = 15
            LEFT_HIP = 23; LEFT_KNEE = 25; LEFT_ANKLE = 27
            RIGHT_SHOULDER = 12; RIGHT_ELBOW = 14; RIGHT_WRIST = 16
            RIGHT_HIP = 24; RIGHT_KNEE = 26; RIGHT_ANKLE = 28
            
            def calculate_angle(a, b, c):
                a = np.array([a['x'], a['y']])
                b = np.array([b['x'], b['y']])
                c = np.array([c['x'], c['y']])
                
                radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
                angle = np.abs(np.degrees(radians))
                return min(angle, 360 - angle)
            
            # Calculate angles
            left_knee_angle = calculate_angle(
                landmarks[LEFT_HIP], landmarks[LEFT_KNEE], landmarks[LEFT_ANKLE]
            )
            left_elbow_angle = calculate_angle(
                landmarks[LEFT_SHOULDER], landmarks[LEFT_ELBOW], landmarks[LEFT_WRIST]
            )
            
            # Determine exercise state
            feedback = []
            state = "standing"
            
            if left_knee_angle < 100:
                state = "squatting"
                feedback.append("🎯 In squat position")
            elif left_knee_angle > 160:
                state = "standing"
                feedback.append("🧍 Standing tall")
            else:
                state = "transition"
                feedback.append("🔄 Moving between positions")
                
            if left_elbow_angle < 90:
                feedback.append("💪 Push-up ready")
                
            # Form quality assessment
            form_score = 100
            if left_knee_angle < 80:
                feedback.append("🔥 Perfect squat depth!")
            elif left_knee_angle > 120 and state == "squatting":
                feedback.append("⬇️ Go deeper for better squat")
                form_score -= 20
                
            return {
                "pose_detected": True,
                "knee_angle": round(left_knee_angle, 1),
                "elbow_angle": round(left_elbow_angle, 1),
                "state": state,
                "feedback": feedback,
                "form_score": form_score,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"pose_detected": False, "error": str(e)}
    
    def get_frame(self):
        """Get current frame as base64"""
        if self.current_frame is not None:
            # Resize for performance
            frame = cv2.resize(self.current_frame, (640, 480))
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                return f"data:image/jpeg;base64,{jpg_as_text}"
        return None
    
    def get_analysis(self):
        """Get latest real analysis"""
        return self.latest_analysis
    
    def stop_camera(self):
        """Stop camera"""
        self.is_running = False
        if self.camera and self.camera_available:
            self.camera.release()
        cv2.destroyAllWindows()
        return {"message": "📹 Camera stopped", "mode": "real_camera"}

# Global instance
camera_processor = RealCameraProcessor()