
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mood Machine Module - Emotion State Machine for Desktop AI Assistant
===================================================================

Manages AI assistant's emotional state transitions based on user events.
Supports 5 emotions: Happy, Angry, Hungry, Sad, Surprised.
"""

import json
import os
from typing import Optional, List, Dict


class MoodMachine:
    """
    Emotion state machine class.
    Manages AI assistant's emotional state transitions.
    """

    # Valid emotion states
    VALID_MOODS = {"happy", "angry", "hungry", "sad", "surprised"}

    def __init__(self, rules_file: str = "rules.json"):
        """
        Initialize mood machine.

        Args:
            rules_file: Path to JSON file containing emotion transition rules
        """
        self.rules_file = rules_file
        self.default_mood = None
        self.rules: List[Dict] = []
        self.current_mood = None

        # Create default rules file if it doesn't exist
        if not os.path.exists(rules_file):
            self._create_default_rules()

        self._load_rules()
        self.current_mood = self.default_mood
        print(f"✓ Mood machine initialized. Current mood: {self.current_mood}")

    def _create_default_rules(self) -> None:
        """Create default rules file."""
        default_rules = {
            "default": "happy",
            "rules": [
                {"event": "cleaned_junk", "to": "happy", "priority": 1},
                {"event": "new_software_installed", "to": "angry", "priority": 1},
                {"event": "idle_30min", "to": "hungry", "priority": 2},
                {"event": "user_scolded", "to": "sad", "priority": 1},
                {"event": "unexpected_gift", "to": "surprised", "priority": 1}
            ]
        }

        with open(self.rules_file, 'w', encoding='utf-8') as f:
            json.dump(default_rules, f, ensure_ascii=False, indent=2)

        print(f"✓ Default rules file created: {self.rules_file}")

    def _load_rules(self) -> None:
        """Load rules from JSON file."""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate default mood
            default_mood = data.get("default")
            if default_mood not in self.VALID_MOODS:
                raise ValueError(f"Default mood '{default_mood}' not in valid moods")

            self.default_mood = default_mood

            # Load and validate rules
            self.rules = []
            for rule in data.get("rules", []):
                if "event" not in rule or "to" not in rule or "priority" not in rule:
                    raise ValueError(f"Invalid rule format: {rule}")

                if rule["to"] not in self.VALID_MOODS:
                    raise ValueError(f"Mood '{rule['to']}' not in valid moods")

                self.rules.append(rule)

            # Sort by priority (lower number = higher priority)
            self.rules.sort(key=lambda x: x.get("priority", float('inf')))

            print(f"✓ Loaded {len(self.rules)} rules")

        except FileNotFoundError:
            raise FileNotFoundError(f"Rules file not found: {self.rules_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in rules file: {self.rules_file}")

    def get_current_mood(self) -> str:
        """
        Get current mood state.

        Returns:
            Current mood string
        """
        return self.current_mood

    def update(self, event: str) -> bool:
        """
        Update mood based on event.

        Args:
            event: Trigger event string

        Returns:
            True if mood was updated, False otherwise
        """
        old_mood = self.current_mood

        # Find matching rule by priority
        for rule in self.rules:
            if rule["event"] == event:
                new_mood = rule["to"]
                self.current_mood = new_mood
                priority = rule.get("priority", "N/A")
                print(f"📢 Event '{event}' triggered (priority: {priority})")
                print(f"   Mood transition: {old_mood} → {new_mood}")
                return True

        print(f"⚠ No rule found for event '{event}'. Mood unchanged: {old_mood}")
        return False

    def reset(self) -> None:
        """Reset mood to default."""
        old_mood = self.current_mood
        self.current_mood = self.default_mood
        print(f"🔄 Reset mood: {old_mood} → {self.default_mood}")

    def list_moods(self) -> List[str]:
        """List all supported moods."""
        return sorted(list(self.VALID_MOODS))

    def list_events(self) -> List[str]:
        """List all available events."""
        return [rule["event"] for rule in self.rules]


def print_separator(title: str = None) -> None:
    """Print a separator line."""
    if title:
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")
    else:
        print(f"\n{'-'*50}\n")


def run_tests() -> None:
    """Run test demo."""
    print_separator("🤖 AI Assistant Mood Machine Demo")

    # Initialize
    print("\n[1] Initializing mood machine...\n")
    mood_machine = MoodMachine("rules.json")

    # Show initial state
    print_separator("Initial State")
    print(f"Current mood: {mood_machine.get_current_mood()}")
    print(f"Supported moods: {', '.join(mood_machine.list_moods())}")
    print(f"Available events: {', '.join(mood_machine.list_events())}")

    # Test events
    print_separator("Event Testing")

    test_events = [
        "cleaned_junk",          # Should become happy
        "user_scolded",          # Should become sad
        "idle_30min",            # Should become hungry
        "new_software_installed", # Should become angry
        "unexpected_gift",       # Should become surprised
        "unknown_event",         # Unknown event, no change
    ]

    for event in test_events:
        print()
        mood_machine.update(event)

    # Test reset
    print_separator("Reset Test")
    print(f"\nBefore reset: {mood_machine.get_current_mood()}")
    mood_machine.reset()
    print(f"After reset: {mood_machine.get_current_mood()}")

    # Interactive demo
    print_separator("Interactive Demo")
    print("\nAvailable events:")
    for i, event in enumerate(mood_machine.list_events(), 1):
        print(f"  {i}. {event}")
    print(f"  0. Exit demo\n")

    while True:
        try:
            choice = input("Select event (0-6): ").strip()

            if choice == "0":
                print("\n👋 Demo ended. Thanks for using!")
                break

            idx = int(choice) - 1
            events = mood_machine.list_events()

            if 0 <= idx < len(events):
                print()
                mood_machine.update(events[idx])
                print(f"Current mood: {mood_machine.get_current_mood()}\n")
            else:
                print("❌ Invalid selection. Please try again.\n")
        except ValueError:
            print("❌ Invalid input. Please enter a number.\n")
        except KeyboardInterrupt:
            print("\n\n👋 Demo ended. Thanks for using!")
            break


if __name__ == "__main__":
    run_tests()
