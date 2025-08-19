"""Sound management system."""
import pygame
from pathlib import Path
from config import Config

class SoundManager:
    """Manages all game sounds and music."""
    
    def __init__(self):
        self.sounds = {}
        self.volume = 0.7
        self.sfx_enabled = True
        self.music_enabled = True
        self.load_sounds()
    
    def load_sounds(self):
        """Load all sound files."""
        print("Loading sounds...")
        print(f"Looking for sounds in: {Config.SOUNDS_DIR}")
        
        for name, path in Config.SOUNDS.items():
            print(f"Trying to load {name} from {path}")
            if path.exists():
                try:
                    sound = pygame.mixer.Sound(str(path))
                    sound.set_volume(self.volume)
                    self.sounds[name] = sound
                    print(f"✓ Loaded sound: {name}")
                except pygame.error as e:
                    print(f"✗ Could not load sound {name}: {e}")
                    self.sounds[name] = None
            else:
                print(f"✗ Sound file not found: {path}")
                # Create a dummy sound for missing files
                self.sounds[name] = None
    
    def play_sound(self, name):
        """Play a sound effect."""
        if not self.sfx_enabled:
            print(f"Sound '{name}' not played - SFX disabled")
            return
        
        if name in self.sounds and self.sounds[name]:
            try:
                self.sounds[name].play()
                print(f"♪ Playing sound: {name}")
            except pygame.error as e:
                print(f"Error playing sound {name}: {e}")
        else:
            print(f"Sound '{name}' not found or not loaded")
    
    def set_volume(self, volume):
        """Set the volume for all sounds (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)
    
    def get_volume(self):
        """Get the current volume."""
        return self.volume
    
    def toggle_sfx(self):
        """Toggle sound effects on/off."""
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled
    
    def is_sfx_enabled(self):
        """Check if sound effects are enabled."""
        return self.sfx_enabled
    
    def toggle_music(self):
        """Toggle music on/off."""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        return self.music_enabled
    
    def is_music_enabled(self):
        """Check if music is enabled."""
        return self.music_enabled
    
    def play_music(self, filename, loops=-1):
        """Play background music."""
        if not self.music_enabled:
            return
        
        music_path = Config.SOUNDS_DIR / filename
        if music_path.exists():
            try:
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.play(loops)
            except pygame.error as e:
                print(f"Could not play music {filename}: {e}")
        else:
            print(f"Music file not found: {music_path}")
    
    def stop_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()