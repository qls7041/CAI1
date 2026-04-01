cat > mood_machine.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情绪状态机模块 - 桌面AI助手的情绪管理系统
============================================

管理AI助手的情绪状态转换，根据用户事件触发情绪变化。
支持5种情绪：开心、生气、饿、委屈、惊讶
"""

import json
import os
from typing import Optional, List, Dict


class MoodMachine:
    """
    情绪状态机类
    管理AI助手的情绪状态转换
    """

    # 有效的情绪状态集合
    VALID_MOODS = {"开心", "生气", "饿", "委屈", "惊讶"}

    def __init__(self, rules_file: str = "rules.json"):
        """
        初始化情绪状态机

        参数:
            rules_file: 情绪转换规则JSON文件路径
        """
        self.rules_file = rules_file
        self.default_mood = None
        self.rules: List[Dict] = []
        self.current_mood = None

        # 如果规则文件不存在，创建默认规则文件
        if not os.path.exists(rules_file):
            self._create_default_rules()

        self._load_rules()
        self.current_mood = self.default_mood
        print(f"✓ 情绪状态机初始化完成，当前情绪：{self.current_mood}")

    def _create_default_rules(self) -> None:
        """创建默认的规则文件"""
        default_rules = {
            "default": "开心",
            "rules": [
                {"event": "cleaned_junk", "to": "开心", "priority": 1},
                {"event": "new_software_installed", "to": "生气", "priority": 1},
                {"event": "idle_30min", "to": "饿", "priority": 2},
                {"event": "user_scolded", "to": "委屈", "priority": 1},
                {"event": "unexpected_gift", "to": "惊讶", "priority": 1}
            ]
        }

        with open(self.rules_file, 'w', encoding='utf-8') as f:
            json.dump(default_rules, f, ensure_ascii=False, indent=2)

        print(f"✓ 已创建默认规则文件：{self.rules_file}")

    def _load_rules(self) -> None:
        """从JSON文件加载规则"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证默认情绪
            default_mood = data.get("default")
            if default_mood not in self.VALID_MOODS:
                raise ValueError(f"默认情绪 '{default_mood}' 不在有效情绪集合中")

            self.default_mood = default_mood

            # 加载并验证规则
            self.rules = []
            for rule in data.get("rules", []):
                if "event" not in rule or "to" not in rule or "priority" not in rule:
                    raise ValueError(f"规则格式不完整：{rule}")

                if rule["to"] not in self.VALID_MOODS:
                    raise ValueError(f"规则中的情绪 '{rule['to']}' 不在有效情绪集合中")

                self.rules.append(rule)

            # 按优先级排序（数字越小优先级越高）
            self.rules.sort(key=lambda x: x.get("priority", float('inf')))

            print(f"✓ 已成功加载 {len(self.rules)} 条规则")

        except FileNotFoundError:
            raise FileNotFoundError(f"规则文件未找到：{self.rules_file}")
        except json.JSONDecodeError:
            raise ValueError(f"规则文件JSON格式错误：{self.rules_file}")

    def get_current_mood(self) -> str:
        """
        获取当前情绪状态

        返回:
            当前情绪字符串
        """
        return self.current_mood

    def update(self, event: str) -> bool:
        """
        根据事件更新情绪状态

        参数:
            event: 触发的事件字符串

        返回:
            是否成功更新情绪（找到匹配的规则）
        """
        old_mood = self.current_mood

        # 按优先级查找匹配的规则
        for rule in self.rules:
            if rule["event"] == event:
                new_mood = rule["to"]
                self.current_mood = new_mood
                priority = rule.get("priority", "未设置")
                print(f"📢 事件 '{event}' 触发 (优先级: {priority})")
                print(f"   情绪转换：{old_mood} → {new_mood}")
                return True

        print(f"⚠ 事件 '{event}' 未找到对应规则，情绪保持不变：{old_mood}")
        return False

    def reset(self) -> None:
        """将情绪重置为默认情绪"""
        old_mood = self.current_mood
        self.current_mood = self.default_mood
        print(f"🔄 已重置情绪：{old_mood} → {self.default_mood}")

    def list_moods(self) -> List[str]:
        """列出所有支持的情绪"""
        return sorted(list(self.VALID_MOODS))

    def list_events(self) -> List[str]:
        """列出所有可用的事件"""
        return [rule["event"] for rule in self.rules]


def print_separator(title: str = None) -> None:
    """打印分隔线"""
    if title:
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")
    else:
        print(f"\n{'-'*50}\n")


def run_tests() -> None:
    """运行测试演示"""
    print_separator("🤖 AI助手情绪状态机演示")

    # 初始化
    print("\n[1] 初始化情绪状态机\n")
    mood_machine = MoodMachine("rules.json")

    # 显示初始信息
    print_separator("初始状态")
    print(f"当前情绪：{mood_machine.get_current_mood()}")
    print(f"支持的情绪：{', '.join(mood_machine.list_moods())}")
    print(f"可用事件：{', '.join(mood_machine.list_events())}")

    # 测试不同事件
    print_separator("事件测试")

    test_events = [
        "cleaned_junk",          # 应该开心
        "user_scolded",          # 应该委屈
        "idle_30min",            # 应该饿
        "new_software_installed", # 应该生气
        "unexpected_gift",       # 应该惊讶
        "unknown_event",         # 未知事件，不变
    ]

    for event in test_events:
        print()
        mood_machine.update(event)

    # 测试重置
    print_separator("重置测试")
    print(f"\n重置前情绪：{mood_machine.get_current_mood()}")
    mood_machine.reset()
    print(f"重置后情绪：{mood_machine.get_current_mood()}")

    # 交互式演示
    print_separator("交互式演示")
    print("\n可用事件：")
    for i, event in enumerate(mood_machine.list_events(), 1):
        print(f"  {i}. {event}")
    print(f"  0. 退出演示\n")

    while True:
        try:
            choice = input("请选择要测试的事件 (0-6)：").strip()

            if choice == "0":
                print("\n👋 演示结束，谢谢使用！")
                break

            idx = int(choice) - 1
            events = mood_machine.list_events()

            if 0 <= idx < len(events):
                print()
                mood_machine.update(events[idx])
                print(f"当前情绪：{mood_machine.get_current_mood()}\n")
            else:
                print("❌ 输入无效，请重新选择\n")
        except ValueError:
            print("❌ 输入格式错误，请输入数字\n")
        except KeyboardInterrupt:
            print("\n\n👋 演示结束，谢谢使用！")
            break


if __name__ == "__main__":
    run_tests()
EOF
