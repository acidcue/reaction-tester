"""Save and load game data including scores, settings, and achievements."""
import json
import os
from datetime import datetime
from pathlib import Path
from config import Config

class SaveManager:
    """Manages persistent game data storage."""
    
    def __init__(self):
        self.ensure_data_directory()
        self.scores_file = Config.DATA_DIR / "scores.json"
        self.settings_file = Config.DATA_DIR / "settings.json"
        self.achievements_file = Config.DATA_DIR / "achievements.json"
        
        self.scores = self.load_scores()
        self.settings = self.load_settings()
        self.achievements = self.load_achievements()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_scores(self):
        """Load score data from file."""
        if self.scores_file.exists():
            try:
                with open(self.scores_file, 'r') as f:
                    data = json.load(f)
                    
                # Check if this is the old format and migrate it
                if "by_difficulty" not in data and ("best_times" in data or "all_attempts" in data):
                    print("Migrating old save format to new difficulty-based format...")
                    return self.migrate_old_format(data)
                
                # Check if we have the new format but missing some difficulties
                if "by_difficulty" in data:
                    # Ensure all difficulties exist
                    for difficulty in ["easy", "normal", "hard", "beast", "twitchy-god"]:
                        if difficulty not in data["by_difficulty"]:
                            data["by_difficulty"][difficulty] = {
                                "best_times": [],
                                "all_attempts": [],
                                "statistics": {
                                    "total_attempts": 0,
                                    "best_time": None,
                                    "average_time": None
                                }
                            }
                    
                    # Ensure overall_statistics exists
                    if "overall_statistics" not in data:
                        data["overall_statistics"] = {
                            "total_attempts": 0,
                            "total_playtime": 0,
                            "favorite_difficulty": "normal"
                        }
                    
                    return data
                
                return data
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading scores: {e}")
        
        # Return default structure with difficulty-separated data
        return self.get_default_scores_structure()
    
    def migrate_old_format(self, old_data):
        """Migrate old save format to new difficulty-based format."""
        new_data = self.get_default_scores_structure()
        
        # Migrate old attempts to "normal" difficulty (since that was the default)
        if "all_attempts" in old_data:
            for attempt in old_data["all_attempts"]:
                # Add difficulty field if missing
                if "difficulty" not in attempt:
                    attempt["difficulty"] = "normal"
                
                difficulty = attempt["difficulty"]
                if difficulty not in new_data["by_difficulty"]:
                    difficulty = "normal"  # Fallback
                
                new_data["by_difficulty"][difficulty]["all_attempts"].append(attempt)
        
        # Migrate old statistics
        if "statistics" in old_data:
            old_stats = old_data["statistics"]
            new_data["by_difficulty"]["normal"]["statistics"] = {
                "total_attempts": old_stats.get("total_attempts", 0),
                "best_time": old_stats.get("best_time", None),
                "average_time": old_stats.get("average_time", None)
            }
            
            # Update overall statistics
            new_data["overall_statistics"]["total_attempts"] = old_stats.get("total_attempts", 0)
        
        # Recalculate best times for each difficulty
        for difficulty, data in new_data["by_difficulty"].items():
            if data["all_attempts"]:
                times = [attempt["time_ms"] for attempt in data["all_attempts"]]
                data["best_times"] = sorted(times)[:20]
        
        # Save the migrated data
        self.scores = new_data
        self.save_scores()
        print("Migration complete!")
        
        return new_data
    
    def get_default_scores_structure(self):
        """Get the default scores data structure."""
        return {
            "by_difficulty": {
                "easy": {
                    "best_times": [],
                    "all_attempts": [],
                    "statistics": {
                        "total_attempts": 0,
                        "best_time": None,
                        "average_time": None
                    }
                },
                "normal": {
                    "best_times": [],
                    "all_attempts": [],
                    "statistics": {
                        "total_attempts": 0,
                        "best_time": None,
                        "average_time": None
                    }
                },
                "hard": {
                    "best_times": [],
                    "all_attempts": [],
                    "statistics": {
                        "total_attempts": 0,
                        "best_time": None,
                        "average_time": None
                    }
                },
                "beast": {
                    "best_times": [],
                    "all_attempts": [],
                    "statistics": {
                        "total_attempts": 0,
                        "best_time": None,
                        "average_time": None
                    }
                },
                "twitchy-god": {
                    "best_times": [],
                    "all_attempts": [],
                    "statistics": {
                        "total_attempts": 0,
                        "best_time": None,
                        "average_time": None
                    }
                }
            },
            "overall_statistics": {
                "total_attempts": 0,
                "total_playtime": 0,
                "favorite_difficulty": "normal"
            }
        }
    
    def save_scores(self):
        """Save score data to file."""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=2)
        except IOError as e:
            print(f"Error saving scores: {e}")
    
    def add_score(self, reaction_time_ms, difficulty="normal"):
        """Add a new reaction time score for a specific difficulty."""
        try:
            timestamp = datetime.now().isoformat()
            
            # Ensure the main structure exists
            if "by_difficulty" not in self.scores:
                self.scores = self.load_scores.__func__(self)  # Reset to default structure
            
            # Ensure difficulty exists in data structure
            if difficulty not in self.scores["by_difficulty"]:
                self.scores["by_difficulty"][difficulty] = {
                    "best_times": [],
                    "all_attempts": [],
                    "statistics": {
                        "total_attempts": 0,
                        "best_time": None,
                        "average_time": None
                    }
                }
            
            difficulty_data = self.scores["by_difficulty"][difficulty]
            
            # Add to difficulty-specific attempts
            attempt = {
                "time_ms": reaction_time_ms,
                "timestamp": timestamp,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "difficulty": difficulty
            }
            difficulty_data["all_attempts"].append(attempt)
            
            # Update difficulty-specific statistics
            stats = difficulty_data["statistics"]
            stats["total_attempts"] += 1
            
            # Update best time for this difficulty
            if stats["best_time"] is None or reaction_time_ms < stats["best_time"]:
                stats["best_time"] = reaction_time_ms
            
            # Update average for this difficulty
            all_times = [attempt["time_ms"] for attempt in difficulty_data["all_attempts"]]
            stats["average_time"] = sum(all_times) / len(all_times)
            
            # Keep only top 20 best times for this difficulty
            difficulty_data["best_times"] = sorted(
                [attempt["time_ms"] for attempt in difficulty_data["all_attempts"]]
            )[:20]
            
            # Limit stored attempts to last 500 per difficulty
            if len(difficulty_data["all_attempts"]) > 500:
                difficulty_data["all_attempts"] = difficulty_data["all_attempts"][-500:]
            
            # Ensure overall_statistics exists
            if "overall_statistics" not in self.scores:
                self.scores["overall_statistics"] = {
                    "total_attempts": 0,
                    "total_playtime": 0,
                    "favorite_difficulty": "normal"
                }
            
            # Update overall statistics
            self.scores["overall_statistics"]["total_attempts"] += 1
            
            # Track favorite difficulty
            difficulty_counts = {}
            for diff, data in self.scores["by_difficulty"].items():
                difficulty_counts[diff] = data["statistics"]["total_attempts"]
            
            if difficulty_counts:
                self.scores["overall_statistics"]["favorite_difficulty"] = max(
                    difficulty_counts, key=difficulty_counts.get
                )
            
            self.save_scores()
            self.check_achievements(reaction_time_ms, difficulty)
            
        except Exception as e:
            print(f"Error in add_score: {e}")
            import traceback
            traceback.print_exc()
    
    def get_best_times(self, difficulty="normal", limit=10):
        """Get the best reaction times for a specific difficulty."""
        try:
            # Ensure scores structure exists
            if "by_difficulty" not in self.scores:
                self.scores = self.get_default_scores_structure()
                self.save_scores()
            
            if difficulty not in self.scores["by_difficulty"]:
                return []
            
            return self.scores["by_difficulty"][difficulty]["best_times"][:limit]
        except Exception as e:
            print(f"Error getting best times for {difficulty}: {e}")
            return []
    
    def get_recent_attempts(self, difficulty="normal", limit=20):
        """Get recent attempts for a specific difficulty."""
        try:
            # Ensure scores structure exists
            if "by_difficulty" not in self.scores:
                self.scores = self.get_default_scores_structure()
                self.save_scores()
            
            if difficulty not in self.scores["by_difficulty"]:
                return []
            
            return self.scores["by_difficulty"][difficulty]["all_attempts"][-limit:]
        except Exception as e:
            print(f"Error getting recent attempts for {difficulty}: {e}")
            return []
    
    def get_statistics(self, difficulty="normal"):
        """Get statistics for a specific difficulty."""
        try:
            # Ensure scores structure exists
            if "by_difficulty" not in self.scores:
                self.scores = self.get_default_scores_structure()
                self.save_scores()
            
            if difficulty not in self.scores["by_difficulty"]:
                return {
                    "total_attempts": 0,
                    "best_time": None,
                    "average_time": None
                }
            
            return self.scores["by_difficulty"][difficulty]["statistics"]
        except Exception as e:
            print(f"Error getting statistics for {difficulty}: {e}")
            return {
                "total_attempts": 0,
                "best_time": None,
                "average_time": None
            }
    
    def get_overall_statistics(self):
        """Get overall statistics across all difficulties."""
        try:
            # Ensure scores structure exists
            if "by_difficulty" not in self.scores:
                self.scores = self.get_default_scores_structure()
                self.save_scores()
            
            if "overall_statistics" not in self.scores:
                self.scores["overall_statistics"] = {
                    "total_attempts": 0,
                    "total_playtime": 0,
                    "favorite_difficulty": "normal"
                }
                self.save_scores()
            
            return self.scores["overall_statistics"]
        except Exception as e:
            print(f"Error getting overall statistics: {e}")
            return {
                "total_attempts": 0,
                "total_playtime": 0,
                "favorite_difficulty": "normal"
            }
    
    def get_all_difficulties_stats(self):
        """Get statistics for all difficulties."""
        stats = {}
        for difficulty in ["easy", "normal", "hard", "beast", "twitchy-god"]:
            if difficulty in self.scores["by_difficulty"]:
                stats[difficulty] = self.scores["by_difficulty"][difficulty]["statistics"]
            else:
                stats[difficulty] = {
                    "total_attempts": 0,
                    "best_time": None,
                    "average_time": None
                }
        return stats
    
    def get_daily_stats(self, difficulty="normal", date_str=None):
        """Get statistics for a specific day and difficulty."""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        if difficulty not in self.scores["by_difficulty"]:
            return None
        
        daily_attempts = [
            attempt for attempt in self.scores["by_difficulty"][difficulty]["all_attempts"]
            if attempt["date"] == date_str
        ]
        
        if not daily_attempts:
            return None
        
        times = [attempt["time_ms"] for attempt in daily_attempts]
        return {
            "date": date_str,
            "difficulty": difficulty,
            "attempts": len(daily_attempts),
            "best_time": min(times),
            "average_time": sum(times) / len(times),
            "total_time": sum(times)
        }
    
    def load_settings(self):
        """Load user settings."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings: {e}")
        
        # Return default settings
        return {
            "sound_volume": 0.7,
            "sfx_enabled": True,
            "music_enabled": True,
            "difficulty": "normal",
            "show_statistics": True,
            "theme": "default",
            "fullscreen": False
        }
    
    def save_settings(self):
        """Save user settings."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def update_setting(self, key, value):
        """Update a specific setting."""
        self.settings[key] = value
        self.save_settings()
    
    def get_setting(self, key, default=None):
        """Get a specific setting value."""
        try:
            return self.settings.get(key, default)
        except Exception as e:
            print(f"Error getting setting {key}: {e}")
            return default
    
    def load_achievements(self):
        """Load achievement data."""
        if self.achievements_file.exists():
            try:
                with open(self.achievements_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading achievements: {e}")
        
        # Return default achievements
        return {
            "unlocked": [],
            "progress": {}
        }
    
    def save_achievements(self):
        """Save achievement data."""
        try:
            with open(self.achievements_file, 'w') as f:
                json.dump(self.achievements, f, indent=2)
        except IOError as e:
            print(f"Error saving achievements: {e}")
    
    def unlock_achievement(self, achievement_id):
        """Unlock an achievement."""
        if achievement_id not in self.achievements["unlocked"]:
            self.achievements["unlocked"].append(achievement_id)
            self.achievements["unlocked"].sort()
            self.save_achievements()
            return True
        return False
    
    def is_achievement_unlocked(self, achievement_id):
        """Check if an achievement is unlocked."""
        return achievement_id in self.achievements["unlocked"]
    
    def check_achievements(self, latest_time_ms):
        """Check and unlock achievements based on latest performance."""
        stats = self.get_statistics()
        achievements_unlocked = []
        
        # Speed achievements
        if latest_time_ms <= 150 and not self.is_achievement_unlocked("lightning_fast"):
            self.unlock_achievement("lightning_fast")
            achievements_unlocked.append("Lightning Fast - Under 150ms!")
        
        if latest_time_ms <= 200 and not self.is_achievement_unlocked("quick_draw"):
            self.unlock_achievement("quick_draw")
            achievements_unlocked.append("Quick Draw - Under 200ms!")
        
        # Consistency achievements
        if stats["total_attempts"] >= 10:
            recent_10 = self.get_recent_attempts(10)
            if len(recent_10) == 10:
                times = [attempt["time_ms"] for attempt in recent_10]
                avg = sum(times) / len(times)
                if avg <= 250 and not self.is_achievement_unlocked("consistent_performer"):
                    self.unlock_achievement("consistent_performer")
                    achievements_unlocked.append("Consistent Performer - 10 attempts under 250ms average!")
        
        # Volume achievements
        if stats["total_attempts"] >= 100 and not self.is_achievement_unlocked("century_club"):
            self.unlock_achievement("century_club")
            achievements_unlocked.append("Century Club - 100 attempts!")
        
        if stats["total_attempts"] >= 500 and not self.is_achievement_unlocked("dedicated_player"):
            self.unlock_achievement("dedicated_player")
            achievements_unlocked.append("Dedicated Player - 500 attempts!")
        
        return achievements_unlocked
    
    def get_achievement_list(self):
        """Get list of all possible achievements with unlock status."""
        all_achievements = {
            "quick_draw": {
                "name": "Quick Draw",
                "description": "React in under 200ms",
                "icon": "⚡"
            },
            "lightning_fast": {
                "name": "Lightning Fast",
                "description": "React in under 150ms",
                "icon": "🔥"
            },
            "consistent_performer": {
                "name": "Consistent Performer",
                "description": "Average under 250ms over 10 attempts",
                "icon": "🎯"
            },
            "century_club": {
                "name": "Century Club",
                "description": "Complete 100 attempts",
                "icon": "💯"
            },
            "dedicated_player": {
                "name": "Dedicated Player",
                "description": "Complete 500 attempts",
                "icon": "🏆"
            }
        }
        
        for achievement_id, data in all_achievements.items():
            data["unlocked"] = self.is_achievement_unlocked(achievement_id)
        
        return all_achievements
    
    def clear_all_data(self):
        """Clear all saved data (use with caution!)."""
        self.scores = self.load_scores.__func__(self)  # Reset to defaults
        self.settings = self.load_settings.__func__(self)
        self.achievements = self.load_achievements.__func__(self)
        
        # Remove files
        for file_path in [self.scores_file, self.settings_file, self.achievements_file]:
            if file_path.exists():
                os.remove(file_path)