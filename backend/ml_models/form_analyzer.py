import numpy as np
from datetime import datetime

class AdvancedFormAnalyzer:
    def __init__(self):
        self.rep_history = []
        self.form_scores = []
        
    def analyze_squat_form(self, angles):
        """Advanced squat form analysis with multiple metrics"""
        feedback = []
        score = 100  # Start with perfect score
        critical_errors = []
        
        avg_knee_angle = (angles['left_knee'] + angles['right_knee']) / 2
        avg_hip_angle = (angles['left_hip'] + angles['right_hip']) / 2
        
        # 1. Depth Analysis (40% of score)
        if avg_knee_angle > 140:
            feedback.append("⬇️ Go deeper for effective squat")
            score -= 20
        elif avg_knee_angle < 80:
            feedback.append("🔥 Excellent depth!")
            score += 5
        elif avg_knee_angle < 100:
            feedback.append("💪 Good squat depth")
        else:
            feedback.append("📏 Adequate depth")
            
        # 2. Posture Analysis (30% of score)
        if avg_hip_angle < 80:
            critical_errors.append("🚨 Back rounding - risk of injury!")
            score -= 30
        elif avg_hip_angle < 100:
            feedback.append("📐 Maintain neutral spine")
            score -= 10
        else:
            feedback.append("✅ Good back posture")
            
        # 3. Symmetry Analysis (30% of score)
        symmetry = self._analyze_symmetry(angles)
        if symmetry['symmetry_score'] < 80:
            feedback.append("⚖️ Work on left-right symmetry")
            score -= 10
        else:
            feedback.append("✅ Good symmetry")
            
        # Add symmetry feedback
        feedback.extend(symmetry['feedback'])
        
        # Combine feedback
        all_feedback = critical_errors + feedback
        
        return {
            "form_score": max(score, 0),
            "feedback": all_feedback,
            "metrics": {
                "depth_angle": avg_knee_angle,
                "back_angle": avg_hip_angle,
                "symmetry_score": symmetry['symmetry_score'],
                "has_critical_errors": len(critical_errors) > 0
            }
        }
    
    def analyze_pushup_form(self, angles):
        """Advanced push-up form analysis"""
        feedback = []
        score = 100
        critical_errors = []
        
        avg_elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2
        
        # 1. Depth Analysis
        if avg_elbow_angle > 120:
            feedback.append("⬇️ Go lower for effective push-up")
            score -= 25
        elif avg_elbow_angle < 90:
            feedback.append("🔥 Chest to ground!")
            score += 5
        else:
            feedback.append("💪 Good depth")
            
        # 2. Body Alignment
        hip_angle = (angles['left_hip'] + angles['right_hip']) / 2
        if hip_angle < 150:
            critical_errors.append("🚨 Don't sag your hips!")
            score -= 30
        elif hip_angle > 170:
            feedback.append("📐 Keep body straight")
            score -= 5
        else:
            feedback.append("✅ Good body alignment")
            
        # 3. Symmetry
        symmetry = self._analyze_symmetry(angles)
        if symmetry['symmetry_score'] < 80:
            feedback.append("⚖️ Arms uneven")
            score -= 10
            
        feedback.extend(symmetry['feedback'])
        all_feedback = critical_errors + feedback
        
        return {
            "form_score": max(score, 0),
            "feedback": all_feedback,
            "metrics": {
                "elbow_angle": avg_elbow_angle,
                "body_alignment": hip_angle,
                "symmetry_score": symmetry['symmetry_score'],
                "has_critical_errors": len(critical_errors) > 0
            }
        }
    
    def _analyze_symmetry(self, angles):
        """Analyze left-right symmetry"""
        knee_diff = abs(angles['left_knee'] - angles['right_knee'])
        elbow_diff = abs(angles['left_elbow'] - angles['right_elbow'])
        hip_diff = abs(angles['left_hip'] - angles['right_hip'])
        
        avg_diff = (knee_diff + elbow_diff + hip_diff) / 3
        symmetry_score = max(0, 100 - avg_diff * 2)
        
        feedback = []
        if knee_diff > 15:
            feedback.append(f"⚖️ Knee difference: {knee_diff:.1f}°")
        if elbow_diff > 20:
            feedback.append(f"⚖️ Elbow difference: {elbow_diff:.1f}°")
        if hip_diff > 10:
            feedback.append(f"⚖️ Hip difference: {hip_diff:.1f}°")
            
        return {
            "symmetry_score": symmetry_score,
            "feedback": feedback
        }
    
    def track_rep_quality(self, rep_data):
        """Track quality over multiple reps"""
        self.rep_history.append({
            'timestamp': datetime.now(),
            'form_score': rep_data['form_score'],
            'metrics': rep_data['metrics']
        })
        
        # Keep only last 20 reps
        if len(self.rep_history) > 20:
            self.rep_history.pop(0)
            
        return self._calculate_progression()
    
    def _calculate_progression(self):
        """Calculate user progression over time"""
        if len(self.rep_history) < 3:
            return {"message": "Collecting more data..."}
            
        recent_scores = [rep['form_score'] for rep in self.rep_history[-5:]]
        avg_recent = np.mean(recent_scores)
        
        if len(self.rep_history) >= 5:
            old_scores = [rep['form_score'] for rep in self.rep_history[:5]]
            avg_old = np.mean(old_scores)
            improvement = avg_recent - avg_old
            
            if improvement > 5:
                return {"trend": "improving", "message": "Great progress! 🚀"}
            elif improvement > 0:
                return {"trend": "slightly_improving", "message": "Steady improvement 💪"}
            elif improvement < -5:
                return {"trend": "declining", "message": "Focus on consistency 📉"}
        
        return {"trend": "stable", "message": "Maintain current form 📊"}