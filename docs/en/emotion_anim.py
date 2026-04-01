
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emotion Animation Module - Emotion-based Animation Loader
==========================================================

Loads emotion-specific animation files for desktop AI assistant.
"""

import os


class EmotionAnim:
    """
    Emotion animation manager class.
    Returns file paths for emotion-specific animations.
    """

    def __init__(self, character: str = "xiaolin"):
        """
        Initialize emotion animation manager.

        Args:
            character: Character name ('xiaolin' or 'xiaoqi')
        """
        self.character = character
        # Map emotions to filenames
        self.emotion_files = {
            "happy": "happy.png",
            "angry": "angry.png",
            "hungry": "hungry.png",
            "sad": "sad.png",
            "surprised": "surprised.png"
        }
        self.default_file = "happy.png"

    def get_emotion_file(self, emotion: str) -> str:
        """
        Get animation file path for specified emotion.

        Args:
            emotion: Emotion name (happy/angry/hungry/sad/surprised)

        Returns:
            Full path to animation file
        """
        filename = self.emotion_files.get(emotion, self.default_file)
        path = os.path.join("emotions", self.character, filename)

        # Fallback to default if file not found
        if not os.path.exists(path):
            print(f"⚠️ Emotion file not found: {path}")
            path = os.path.join("emotions", self.character, self.default_file)

        return path

    def set_character(self, character: str):
        """
        Switch character.

        Args:
            character: New character name
        """
        self.character = character


# Test code
if __name__ == "__main__":
    anim = EmotionAnim("xiaolin")
    print("XiaoLin happy:", anim.get_emotion_file("happy"))
    print("XiaoLin angry:", anim.get_emotion_file("angry"))

    anim.set_character("xiaoqi")
    print("XiaoQi happy:", anim.get_emotion_file("happy"))
