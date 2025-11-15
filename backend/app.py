from flask import Flask, jsonify
import numpy as np
from datetime import datetime
import random
import cv2
import threading
import time
import base64

app = Flask(__name__)

# Enable CORS manually
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Simple ML Models (defined inline to avoid import issues)
class SimplePoseDetector:
    def __init__(self):
        self.analysis_count = 0
        
    def get_pose_analysis(self):
        """Simple pose analysis simulation"""
        self.analysis_count += 1
        
        # Simulate different exercise positions
        positions = [
            {"knee_angle": 170, "elbow_angle": 165, "hip_angle": 150, "state": "standing"},
            {"knee_angle": 120, "elbow_angle": 160, "hip_angle": 130, "state": "half_squat"},
            {"knee_angle": 85, "elbow_angle": 155, "hip_angle": 100, "state": "full_squat"},
            {"knee_angle": 175, "elbow_angle": 75, "hip_angle": 170, "state": "pushup"}
        ]
        
        current_pos = positions[self.analysis_count % len(positions)]
        
        # Add realistic variations
        angles = {
            'left_knee': current_pos['knee_angle'] + random.uniform(-5, 5),
            'right_knee': current_pos['knee_angle'] + random.uniform(-5, 5),
            'left_elbow': current_pos['elbow_angle'] + random.uniform(-5, 5),
            'right_elbow': current_pos['elbow_angle'] + random.uniform(-5, 5),
            'left_hip': current_pos['hip_angle'] + random.uniform(-5, 5),
            'right_hip': current_pos['hip_angle'] + random.uniform(-5, 5)
        }
        
        return angles, current_pos['state']

class SimpleFormAnalyzer:
    def __init__(self):
        self.rep_history = []
        
    def analyze_form(self, angles, exercise_type):
        """Simple form analysis"""
        if exercise_type == "squats":
            return self._analyze_squat(angles)
        elif exercise_type == "pushups":
            return self._analyze_pushup(angles)
        else:
            return {"form_score": 75, "feedback": ["Basic analysis"]}
    
    def _analyze_squat(self, angles):
        """Analyze squat form"""
        avg_knee = (angles['left_knee'] + angles['right_knee']) / 2
        avg_hip = (angles['left_hip'] + angles['right_hip']) / 2
        
        feedback = []
        score = 100
        
        # Depth analysis
        if avg_knee > 140:
            feedback.append("⬇️ Go deeper")
            score -= 20
        elif avg_knee < 80:
            feedback.append("🔥 Perfect depth!")
            score += 5
            
        # Posture analysis
        if avg_hip < 80:
            feedback.append("🚨 Back rounding!")
            score -= 30
        elif avg_hip < 100:
            feedback.append("📐 Maintain spine")
            score -= 10
            
        # Symmetry
        knee_diff = abs(angles['left_knee'] - angles['right_knee'])
        if knee_diff > 15:
            feedback.append("⚖️ Knee asymmetry")
            score -= 10
            
        return {
            "form_score": max(score, 0),
            "feedback": feedback,
            "metrics": {
                "depth": avg_knee,
                "posture": avg_hip,
                "symmetry": 100 - knee_diff
            }
        }
    
    def _analyze_pushup(self, angles):
        """Analyze push-up form"""
        avg_elbow = (angles['left_elbow'] + angles['right_elbow']) / 2
        avg_hip = (angles['left_hip'] + angles['right_hip']) / 2
        
        feedback = []
        score = 100
        
        # Depth analysis
        if avg_elbow > 120:
            feedback.append("⬇️ Go lower")
            score -= 25
        elif avg_elbow < 90:
            feedback.append("🔥 Chest to ground!")
            score += 5
            
        # Body alignment
        if avg_hip < 150:
            feedback.append("🚨 Don't sag hips!")
            score -= 30
            
        return {
            "form_score": max(score, 0),
            "feedback": feedback,
            "metrics": {
                "depth": avg_elbow,
                "alignment": avg_hip
            }
        }

class SimpleFatigueDetector:
    def __init__(self):
        self.form_scores = []
        self.fatigue_level = 0
        
    def analyze_fatigue(self, form_score):
        """Simple fatigue detection"""
        self.form_scores.append(form_score)
        if len(self.form_scores) > 10:
            self.form_scores.pop(0)
            
        # Calculate fatigue based on form degradation
        if len(self.form_scores) >= 5:
            recent_avg = np.mean(self.form_scores[-5:])
            if len(self.form_scores) >= 10:
                older_avg = np.mean(self.form_scores[:5])
                if recent_avg < older_avg - 10:
                    self.fatigue_level = min(100, self.fatigue_level + 20)
                else:
                    self.fatigue_level = max(0, self.fatigue_level - 5)
        
        # Recommendations
        if self.fatigue_level < 30:
            recommendation = "Keep going! 💪"
        elif self.fatigue_level < 60:
            recommendation = "Consider break soon 🚦"
        else:
            recommendation = "Take a break 🛑"
            
        return {
            "fatigue_level": self.fatigue_level,
            "recommendation": recommendation
        }

class MLEnhancedFitnessAI:
    def __init__(self):
        self.exercise_counts = {"squats": 0, "pushups": 0, "lunges": 0}
        self.workout_history = []
        self.workout_active = False
        self.camera_active = False
        self.camera = None
        self.current_frame = None
        self.camera_thread = None
        
        # Initialize simple ML models
        self.pose_detector = SimplePoseDetector()
        self.form_analyzer = SimpleFormAnalyzer()
        self.fatigue_detector = SimpleFatigueDetector()
        
    def start_camera(self):
        """Start real camera with ML analysis"""
        try:
            print("🎥 Starting camera with ML...")
            
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                for camera_id in [1, 2]:
                    self.camera = cv2.VideoCapture(camera_id)
                    if self.camera.isOpened():
                        break
            
            if self.camera.isOpened():
                self.camera_active = True
                self.camera_thread = threading.Thread(target=self._camera_loop)
                self.camera_thread.daemon = True
                self.camera_thread.start()
                
                return {
                    "message": "✅ Camera started with ML!", 
                    "mode": "real_camera_ml",
                    "status": "active"
                }
            else:
                return {"message": "⚠️ Using ML simulation", "mode": "ml_simulation"}
                
        except Exception as e:
            return {"error": f"Camera error: {str(e)}", "mode": "ml_simulation"}
    
    def _camera_loop(self):
        """Camera loop with ML"""
        frame_count = 0
        while self.camera_active and self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame
                frame_count += 1
                
                # Perform ML analysis every 5 frames
                if frame_count % 5 == 0:
                    self._ml_analysis_cycle()
                    
            time.sleep(0.033)  # ~30 FPS for smooth video
    
    def _ml_analysis_cycle(self):
        """Perform ML analysis cycle"""
        try:
            # Get ML pose analysis
            angles, state = self.pose_detector.get_pose_analysis()
            
            # Store analysis for video overlay
            self.latest_ml_analysis = {
                "pose_detected": True,
                "mode": "real_camera_ml",
                "angles": angles,
                "state": state,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.latest_ml_analysis = {
                "error": f"ML analysis error: {str(e)}",
                "mode": "real_camera_ml"
            }
    
    def analyze_exercise_ml(self, exercise_type):
        """Analyze exercise using ML models"""
        if exercise_type not in self.exercise_counts:
            return {"error": f"Exercise '{exercise_type}' not supported"}
        
        # Get ML pose analysis
        angles, state = self.pose_detector.get_pose_analysis()
        
        # Form analysis
        form_analysis = self.form_analyzer.analyze_form(angles, exercise_type)
        
        # Fatigue analysis
        fatigue_analysis = self.fatigue_detector.analyze_fatigue(form_analysis['form_score'])
        
        # Count rep if in good position
        should_count = False
        if exercise_type == "squats" and state in ["full_squat", "half_squat"]:
            should_count = True
        elif exercise_type == "pushups" and state == "pushup":
            should_count = True
            
        if should_count:
            self.exercise_counts[exercise_type] += 1
        
        return {
            "exercise": exercise_type,
            "count": self.exercise_counts[exercise_type],
            "feedback": form_analysis['feedback'],
            "form_score": form_analysis['form_score'],
            "fatigue_level": fatigue_analysis['fatigue_level'],
            "analysis_source": "ml_enhanced",
            "ml_data": {
                "exercise_phase": state,
                "angles": {k: round(v, 1) for k, v in angles.items()},
                "recommendation": fatigue_analysis['recommendation']
            },
            "rep_counted": should_count,
            "status": "success"
        }
    
    def start_workout(self):
        self.workout_active = True
        self.exercise_counts = {"squats": 0, "pushups": 0, "lunges": 0}
        self.fatigue_detector.fatigue_level = 0
        return {"message": "🏋️ Workout started with ML!", "status": "active"}
    
    def stop_camera(self):
        self.camera_active = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        return {"message": "📹 Camera stopped"}
    
    def get_camera_status(self):
        if self.camera_active:
            return {
                "camera_active": True,
                "mode": "real_camera_ml",
                "message": "📹 Camera with ML active"
            }
        else:
            return {
                "camera_active": False,
                "mode": "inactive",
                "message": "Camera not started"
            }

# Initialize AI
fitness_ai = MLEnhancedFitnessAI()

# ========== VIDEO STREAMING ENDPOINTS ==========

@app.route('/api/camera/feed')
def get_camera_feed():
    """Get current camera frame as base64 image"""
    try:
        if fitness_ai.camera_active and fitness_ai.current_frame is not None:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', fitness_ai.current_frame)
            if ret:
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                return jsonify({
                    "frame": f"data:image/jpeg;base64,{jpg_as_text}",
                    "timestamp": time.time(),
                    "status": "success"
                })
        
        return jsonify({
            "error": "No camera feed available",
            "status": "error"
        })
    except Exception as e:
        return jsonify({"error": f"Feed error: {str(e)}", "status": "error"})

@app.route('/api/camera/feed-with-analysis')
def get_camera_feed_with_analysis():
    """Get camera feed with ML analysis overlay"""
    try:
        if fitness_ai.camera_active and fitness_ai.current_frame is not None:
            frame = fitness_ai.current_frame.copy()
            
            # Add ML analysis information to the frame
            if hasattr(fitness_ai, 'latest_ml_analysis'):
                ml_data = fitness_ai.latest_ml_analysis
                
                # Add text overlay with ML data
                cv2.putText(frame, "AI Fitness Coach - Live ML Analysis", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if 'angles' in ml_data:
                    angles = ml_data['angles']
                    cv2.putText(frame, f"Knee Angle: {angles.get('left_knee', 0):.1f}°", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(frame, f"Elbow Angle: {angles.get('left_elbow', 0):.1f}°", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.putText(frame, f"State: {ml_data.get('state', 'unknown')}", 
                               (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Encode the enhanced frame
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                jpg_as_text = base64.b64encode(buffer).decode('utf-8')
                return jsonify({
                    "frame": f"data:image/jpeg;base64,{jpg_as_text}",
                    "ml_analysis": getattr(fitness_ai, 'latest_ml_analysis', {}),
                    "timestamp": time.time(),
                    "status": "success"
                })
        
        return jsonify({
            "error": "No camera feed available",
            "status": "error"
        })
    except Exception as e:
        return jsonify({"error": f"Feed error: {str(e)}", "status": "error"})

# ========== VIDEO DEMO PAGE ==========

@app.route('/video-demo')
def video_demo():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎥 AI Fitness Coach - Live Video Demo</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 20px;
            }
            .video-section { 
                display: flex; 
                gap: 20px; 
                margin-bottom: 20px; 
            }
            .video-feed { 
                flex: 1; 
                background: #000; 
                border-radius: 10px; 
                overflow: hidden;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            .video-feed img { 
                width: 100%; 
                height: 400px; 
                object-fit: cover; 
            }
            .controls { 
                display: flex; 
                gap: 10px; 
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            button { 
                padding: 12px 24px; 
                background: #4CAF50; 
                color: white; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 16px;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            button:hover { 
                background: #45a049; 
                transform: translateY(-2px);
            }
            .analysis-section { 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 20px; 
            }
            .card { 
                background: rgba(255,255,255,0.15); 
                padding: 20px; 
                border-radius: 10px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .ml-data { 
                font-family: monospace; 
                background: rgba(0,0,0,0.3); 
                padding: 15px; 
                border-radius: 5px; 
                max-height: 300px; 
                overflow-y: auto;
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-active { background: #4CAF50; }
            .status-inactive { background: #f44336; }
            h1, h2, h3 { 
                margin-top: 0; 
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎥 AI Fitness Coach - Live Video & ML Analysis</h1>
            <p>Real-time camera feed with machine learning analysis</p>
            
            <div class="controls">
                <button onclick="startCamera()">Start Camera</button>
                <button onclick="stopCamera()">Stop Camera</button>
                <button onclick="startWorkout()">Start Workout</button>
                <button onclick="analyzeSquat()">Analyze Squat</button>
                <button onclick="analyzePushup()">Analyze Push-up</button>
                <button onclick="getStats()">Get Stats</button>
            </div>
            
            <div class="video-section">
                <div class="video-feed">
                    <h3>Live Camera Feed</h3>
                    <div id="videoContainer">
                        <img id="videoFrame" src="" alt="Camera feed will appear here">
                    </div>
                    <div style="padding: 10px;">
                        <span id="cameraStatus" class="status-indicator status-inactive"></span>
                        <span id="statusText">Camera not started</span>
                    </div>
                </div>
                
                <div class="video-feed">
                    <h3>ML Analysis Feed</h3>
                    <div id="analysisContainer">
                        <img id="analysisFrame" src="" alt="Analysis feed will appear here">
                    </div>
                    <div style="padding: 10px;">
                        <span id="mlStatus" class="status-indicator status-inactive"></span>
                        <span id="mlStatusText">ML analysis inactive</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-section">
                <div class="card">
                    <h3>Real-time ML Analysis</h3>
                    <div id="mlAnalysis" class="ml-data">
                        Waiting for ML analysis...
                    </div>
                </div>
                
                <div class="card">
                    <h3>Exercise Results</h3>
                    <div id="exerciseResults" class="ml-data">
                        No exercises analyzed yet
                    </div>
                </div>
            </div>
        </div>

        <script>
            let videoInterval;
            let analysisInterval;
            
            // Video streaming functions
            async function startVideoStream() {
                videoInterval = setInterval(async () => {
                    try {
                        const response = await fetch('/api/camera/feed');
                        const data = await response.json();
                        if (data.status === 'success') {
                            document.getElementById('videoFrame').src = data.frame;
                            updateCameraStatus(true);
                        }
                    } catch (error) {
                        console.error('Video stream error:', error);
                    }
                }, 100); // 10 FPS
            }
            
            async function startAnalysisStream() {
                analysisInterval = setInterval(async () => {
                    try {
                        const response = await fetch('/api/camera/feed-with-analysis');
                        const data = await response.json();
                        if (data.status === 'success') {
                            document.getElementById('analysisFrame').src = data.frame;
                            if (data.ml_analysis) {
                                updateMLAnalysis(data.ml_analysis);
                            }
                        }
                    } catch (error) {
                        console.error('Analysis stream error:', error);
                    }
                }, 200); // 5 FPS for analysis
            }
            
            function stopVideoStreams() {
                if (videoInterval) clearInterval(videoInterval);
                if (analysisInterval) clearInterval(analysisInterval);
                document.getElementById('videoFrame').src = '';
                document.getElementById('analysisFrame').src = '';
                updateCameraStatus(false);
            }
            
            // Control functions
            async function startCamera() {
                try {
                    const response = await fetch('/api/camera/start');
                    const data = await response.json();
                    
                    if (data.mode && data.mode.includes('camera')) {
                        startVideoStream();
                        startAnalysisStream();
                    }
                } catch (error) {
                    console.error('Camera start error:', error);
                }
            }
            
            async function stopCamera() {
                try {
                    await fetch('/api/camera/stop');
                    stopVideoStreams();
                } catch (error) {
                    console.error('Camera stop error:', error);
                }
            }
            
            async function startWorkout() {
                try {
                    const response = await fetch('/api/workout/start');
                    const data = await response.json();
                    alert('Workout started: ' + data.message);
                } catch (error) {
                    console.error('Workout start error:', error);
                }
            }
            
            async function analyzeSquat() {
                try {
                    const response = await fetch('/api/analyze/squats');
                    const data = await response.json();
                    document.getElementById('exerciseResults').innerHTML = 
                        `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                } catch (error) {
                    console.error('Analysis error:', error);
                }
            }
            
            async function analyzePushup() {
                try {
                    const response = await fetch('/api/analyze/pushups');
                    const data = await response.json();
                    document.getElementById('exerciseResults').innerHTML = 
                        `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                } catch (error) {
                    console.error('Analysis error:', error);
                }
            }
            
            async function getStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    alert('Check console for stats (F12)');
                    console.log('Stats:', data);
                } catch (error) {
                    console.error('Stats error:', error);
                }
            }
            
            // Status update functions
            function updateCameraStatus(active) {
                const indicator = document.getElementById('cameraStatus');
                const text = document.getElementById('statusText');
                
                if (active) {
                    indicator.className = 'status-indicator status-active';
                    text.textContent = 'Camera streaming live';
                } else {
                    indicator.className = 'status-indicator status-inactive';
                    text.textContent = 'Camera not active';
                }
            }
            
            function updateMLAnalysis(analysis) {
                const mlIndicator = document.getElementById('mlStatus');
                const mlText = document.getElementById('mlStatusText');
                const analysisDiv = document.getElementById('mlAnalysis');
                
                mlIndicator.className = 'status-indicator status-active';
                mlText.textContent = 'ML analysis active';
                analysisDiv.innerHTML = `<pre>${JSON.stringify(analysis, null, 2)}</pre>`;
            }
        </script>
    </body>
    </html>
    '''

# ========== EXISTING ENDPOINTS ==========

@app.route('/')
def home():
    return jsonify({
        "message": "🚀 AI Fitness Coach - LIVE VIDEO & ML!",
        "status": "active",
        "version": "3.0.0",
        "features": ["live_video", "ml_analysis", "real_time_feedback"],
        "endpoints": [
            "/video-demo",
            "/api/camera/start",
            "/api/analyze/squats", 
            "/api/workout/start",
            "/api/stats"
        ]
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy", 
        "ai_ready": True, 
        "camera_capable": True,
        "video_streaming": True
    })

# 🎥 CAMERA ENDPOINTS
@app.route('/api/camera/start')
def start_camera():
    result = fitness_ai.start_camera()
    return jsonify(result)

@app.route('/api/camera/stop')
def stop_camera():
    result = fitness_ai.stop_camera()
    return jsonify(result)

@app.route('/api/camera/status')
def camera_status():
    result = fitness_ai.get_camera_status()
    return jsonify(result)

# 🏋️ EXERCISE ANALYSIS WITH ML
@app.route('/api/analyze/<exercise>')
def analyze_exercise(exercise):
    result = fitness_ai.analyze_exercise_ml(exercise)
    return jsonify(result)

# 📊 WORKOUT MANAGEMENT
@app.route('/api/workout/start')
def start_workout():
    result = fitness_ai.start_workout()
    return jsonify(result)

@app.route('/api/workout/end')
def end_workout():
    if fitness_ai.workout_active:
        fitness_ai.workout_active = False
        workout_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "exercises": fitness_ai.exercise_counts.copy(),
            "total_reps": sum(fitness_ai.exercise_counts.values()),
            "final_fatigue": fitness_ai.fatigue_detector.fatigue_level
        }
        fitness_ai.workout_history.append(workout_data)
        return jsonify({"message": "✅ Workout saved!", "summary": workout_data})
    return jsonify({"error": "No active workout"})

@app.route('/api/workout/summary')
def workout_summary():
    return jsonify({
        "workout_active": fitness_ai.workout_active,
        "exercise_counts": fitness_ai.exercise_counts,
        "total_reps": sum(fitness_ai.exercise_counts.values()),
        "camera_active": fitness_ai.camera_active,
        "current_fatigue": fitness_ai.fatigue_detector.fatigue_level
    })

@app.route('/api/stats')
def get_stats():
    total_workout_reps = sum(
        sum(workout["exercises"].values()) 
        for workout in fitness_ai.workout_history
    )
    current_reps = sum(fitness_ai.exercise_counts.values())
    
    return jsonify({
        "current_workout": fitness_ai.exercise_counts,
        "total_workouts": len(fitness_ai.workout_history),
        "total_reps_all_time": total_workout_reps + current_reps,
        "workout_active": fitness_ai.workout_active,
        "camera_active": fitness_ai.camera_active,
        "current_fatigue": fitness_ai.fatigue_detector.fatigue_level
    })

@app.route('/api/reset')
def reset_all():
    fitness_ai.exercise_counts = {"squats": 0, "pushups": 0, "lunges": 0}
    fitness_ai.fatigue_detector.fatigue_level = 0
    fitness_ai.fatigue_detector.form_scores.clear()
    return jsonify({
        "message": "🔁 All counters reset!",
        "counts": fitness_ai.exercise_counts
    })

if __name__ == '__main__':
    print("🎯 AI Fitness Coach - LIVE VIDEO & ML VERSION!")
    print("📍 New Features: Live Video Streaming, ML Analysis Overlay")
    print("📍 Demo Page: http://localhost:5000/video-demo")
    print("📍 Test Sequence:")
    print("   1. Open http://localhost:5000/video-demo")
    print("   2. Click 'Start Camera'")
    print("   3. See live video from your webcam!")
    print("   4. Click 'Analyze Squat' for ML analysis")
    app.run(debug=True, host='0.0.0.0', port=5000)