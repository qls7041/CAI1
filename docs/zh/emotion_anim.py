cat > emotion_anim.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表情动画模块 - 基于情绪的动画加载器
======================================

根据情绪状态返回对应的动画文件路径
"""

import os


class EmotionAnim:
    """
    表情动画管理器类
    根据情绪返回对应的动画文件路径
    """

    def __init__(self, character: str = "xiaolin"):
        """
        初始化表情动画管理器

        参数:
            character: 角色名称（'xiaolin' 或 'xiaoqi'）
        """
        self.character = character
        # 情绪到文件名的映射
        self.emotion_files = {
            "开心": "happy.png",
            "生气": "angry.png",
            "饿": "hungry.png",
            "委屈": "sad.png",
            "惊讶": "surprised.png"
        }
        self.default_file = "happy.png"

    def get_emotion_file(self, emotion: str) -> str:
        """
        根据情绪返回对应的动画文件路径

        参数:
            emotion: 情绪名称（开心/生气/饿/委屈/惊讶）

        返回:
            动画文件的完整路径
        """
        filename = self.emotion_files.get(emotion, self.default_file)
        path = os.path.join("emotions", self.character, filename)

        # 如果文件不存在，打印警告并返回默认
        if not os.path.exists(path):
            print(f"⚠️ 找不到表情文件: {path}")
            path = os.path.join("emotions", self.character, self.default_file)

        return path

    def set_character(self, character: str):
        """
        切换角色

        参数:
            character: 新的角色名称
        """
        self.character = character


# 测试代码
if __name__ == "__main__":
    anim = EmotionAnim("xiaolin")
    print("小麟开心图路径:", anim.get_emotion_file("开心"))
    print("小麟生气图路径:", anim.get_emotion_file("生气"))

    anim.set_character("xiaoqi")
    print("小麒开心图路径:", anim.get_emotion_file("开心"))
EOF
