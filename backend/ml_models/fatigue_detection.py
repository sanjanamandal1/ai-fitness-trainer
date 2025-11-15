import numpy as np
from collections import deque
import time

class FatigueDetector:
    def __init__(self, window_size=8):
        self.window_size = window_size
        self.form_scores = deque(maxlen=window_size)
        self.rep_times = deque(maxlen=window_size)
        self.fatigue_level = 0
        self.last_rep_time = None
        
    def analyze_fatigue(self, current_form_score):
        """Detect fatigue based on form degradation and timing"""
        current_time = time.time()
        
        # Track form scores
        self.form_scores.append(current_form_score)
        
        # Track rep timing
        if self.last_rep_time is not None:
            rep_duration = current_time - self.last_rep_time
            self.rep_times.append(rep_duration)
        self.last_rep_time = current_time
        
        # Calculate fatigue indicators
        fatigue_score = 0
        
        # 1. Form degradation (50% weight)
        if len(self.form_scores) >= 3:
            recent_avg = np.mean(list(self.form_scores)[-3:])
            if len(self.form_scores) >= 6:
                older_avg = np.mean(list(self.form_scores)[-6:-3])
                form_decline = older_avg - recent_avg
                if form_decline > 10:
                    fatigue_score += 50
                elif form_decline > 5:
                    fatigue_score += 25
        
        # 2. Slowing pace (30% weight)
        if len(self.rep_times) >= 3:
            recent_times = list(self.rep_times)[-3:]
            if len(self.rep_times) >= 6:
                older_times = list(self.rep_times)[-6:-3]
                if older_times and recent_times:
                    pace_slowdown = (np.mean(recent_times) - np.mean(older_times)) / np.mean(older_times)
                    if pace_slowdown > 0.3:  # 30% slower
                        fatigue_score += 30
                    elif pace_slowdown > 0.15:  # 15% slower
                        fatigue_score += 15
        
        # 3. Low absolute form score (20% weight)
        if current_form_score < 60:
            fatigue_score += 20
        elif current_form_score < 70:
            fatigue_score += 10
            
        self.fatigue_level = min(100, fatigue_score)
        
        return {
            "fatigue_level": self.fatigue_level,
            "indicators": {
                "form_degradation": fatigue_score >= 25,
                "slowing_pace": fatigue_score >= 15 and len(self.rep_times) >= 3,
                "low_form_score": current_form_score < 70
            },
            "recommendation": self._get_fatigue_recommendation()
        }
    
    def _get_fatigue_recommendation(self):
        """Get recommendation based on fatigue level"""
        if self.fatigue_level < 25:
            return "Keep going! You're doing great! 💪"
        elif self.fatigue_level < 50:
            return "Consider taking a short break soon 🚦"
        elif self.fatigue_level < 75:
            return "Recommended to take a break - form is declining 📉"
        else:
            return "Stop now - high fatigue detected to prevent injury 🛑"
    
    def reset_fatigue(self):
        """Reset fatigue tracking"""
        self.form_scores.clear()
        self.rep_times.clear()
        self.fatigue_level = 0
        self.last_rep_time = None