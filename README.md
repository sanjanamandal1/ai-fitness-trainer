
# 🏋️ AI Fitness Trainer - Real-time AI Personal Coach

A sophisticated fitness coaching platform that uses computer vision and machine learning to analyze exercise form in real-time.

## 🚀 Features

- **Real-time Pose Analysis** - ML-powered joint angle detection
- **Live Video Streaming** - Webcam integration with ML overlay
- **Form Quality Scoring** - Advanced exercise form assessment
- **Fatigue Detection** - AI-based performance monitoring
- **Workout Tracking** - Session management and progress analytics
- **Professional Web Interface** - Real-time feedback dashboard

## 🛠️ Technology Stack

- **Backend**: Flask + Python
- **Computer Vision**: OpenCV
- **Machine Learning**: Custom ML models (Pose, Form, Fatigue)
- **Frontend**: HTML5 + JavaScript + WebSockets
- **Real-time Processing**: Multi-threading

## 🎯 ML Models Implemented

1. **Pose Detector** - Real-time joint angle analysis
2. **Form Analyzer** - Exercise-specific form scoring
3. **Fatigue Detector** - Performance degradation tracking

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/your-username/ai-fitness-trainergit
cd ai-fitness-trainer/backend

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open in browser
http://localhost:5000/video-demo
