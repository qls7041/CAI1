
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XiaoLin AI - Intelligent Desktop Assistant v2.0
================================================

A fully offline, zero-dependency AI conversation engine with:
- 10-level intent priority system
- File management module
- Emotion recognition
- Context memory

Built for Qilin Republic project | Termux compatible | MIT License
"""

import json
import os
import re
import shutil
import time
import random
from pathlib import Path
from difflib import SequenceMatcher


class FileManager:
    """File management module - handles organizing, moving, deleting, and searching files"""

    def __init__(self):
        """Initialize file manager with default Android storage paths"""
        self.download_dir = "/storage/emulated/0/Download"
        self.pictures_dir = "/storage/emulated/0/Pictures"
        self.documents_dir = "/storage/emulated/0/Documents"
        self.backup_dir = "/storage/emulated/0/qlsf/backup"

        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)

    def get_file_type(self, filename: str) -> str:
        """
        Determine file type based on extension

        Args:
            filename: Name of the file

        Returns:
            File type category (image/document/video/archive/temp/other)
        """
        ext = os.path.splitext(filename)[1].lower()

        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return 'image'
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.md', '.xls', '.xlsx', '.ppt', '.pptx']:
            return 'document'
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']:
            return 'video'
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
            return 'archive'
        elif ext in ['.tmp', '.cache', '.log', '.temp']:
            return 'temp'
        else:
            return 'other'

    def organize_downloads(self) -> dict:
        """
        Organize download folder by file type

        Returns:
            Dictionary with file types as keys and file lists as values
        """
        result = {
            "image": [],
            "document": [],
            "video": [],
            "archive": [],
            "temp": [],
            "other": []
        }

        try:
            for file in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, file)
                if os.path.isfile(file_path):
                    file_type = self.get_file_type(file)
                    result[file_type].append(file)
        except Exception:
            return None

        return result

    def move_files_by_type(self, file_type: str, target_dir: str) -> int:
        """
        Move all files of a specific type to target directory

        Args:
            file_type: Type of files to move
            target_dir: Destination directory path

        Returns:
            Number of files successfully moved
        """
        moved = 0
        try:
            os.makedirs(target_dir, exist_ok=True)
            for file in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, file)
                if os.path.isfile(file_path) and self.get_file_type(file) == file_type:
                    try:
                        shutil.move(file_path, os.path.join(target_dir, file))
                        moved += 1
                    except Exception:
                        pass
        except Exception:
            pass
        return moved

    def delete_temp_files(self) -> int:
        """
        Delete all temporary files in download folder

        Returns:
            Number of files deleted
        """
        deleted = 0
        try:
            for file in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, file)
                if os.path.isfile(file_path) and self.get_file_type(file) == 'temp':
                    try:
                        os.remove(file_path)
                        deleted += 1
                    except Exception:
                        pass
        except Exception:
            pass
        return deleted

    def search_files(self, keyword: str) -> list:
        """
        Search for files containing keyword in filename

        Args:
            keyword: Search keyword

        Returns:
            List of matching filenames
        """
        results = []
        try:
            for file in os.listdir(self.download_dir):
                if keyword.lower() in file.lower():
                    results.append(file)
        except Exception:
            pass
        return results

    def get_file_count(self) -> int:
        """
        Get total number of files in download folder

        Returns:
            File count
        """
        count = 0
        try:
            for file in os.listdir(self.download_dir):
                if os.path.isfile(os.path.join(self.download_dir, file)):
                    count += 1
        except Exception:
            pass
        return count

    def delete_file(self, filename: str) -> bool:
        """
        Delete a specific file

        Args:
            filename: Name of file to delete

        Returns:
            True if successful, False otherwise
        """
        file_path = os.path.join(self.download_dir, filename)
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False

    def backup_conversation(self, conversation: list, memory: dict) -> str:
        """
        Backup conversation history to JSON file

        Args:
            conversation: List of conversation entries
            memory: User memory dictionary

        Returns:
            Path to backup file, or None if failed
        """
        try:
            backup_data = {
                "memory": memory,
                "conversation": conversation[-100:],
                "backup_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            backup_filename = "backup_" + time.strftime("%Y%m%d_%H%M%S") + ".json"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            return backup_path
        except Exception:
            return None


class XiaoLinAI:
    """XiaoLin AI - Main conversation engine class"""

    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        """
        Initialize XiaoLin AI

        Args:
            knowledge_base_path: Path to knowledge base JSON file
        """
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()
        self.conversation = []
        self.memory = {
            "user_name": None,
            "last_topic": None,
            "last_correction": None,
            "topics_history": []
        }
        self.file_manager = FileManager()

        # AI personality settings
        self.personality = {
            "name": "XiaoLin",
            "emoji": "🦁",
            "age": "newborn",
            "origin": "Qilin Republic"
        }

    def _load_knowledge_base(self) -> dict:
        """
        Load knowledge base from JSON file

        Returns:
            Knowledge base dictionary, empty structure if file not found
        """
        try:
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"categories": []}

    def detect_intent(self, text: str) -> tuple:
        """
        10-level intent priority detection system

        Priority order (0 highest, 9 lowest):
        0: Emotion (sad, tired, anxious, happy, thanks)
        1: Praise (smart, great, awesome)
        2: Small talk (food, sleep, weather, greeting)
        3: Correction (no, wrong, actually)
        4: About self (who are you, what's your name)
        5: File command (organize, delete, backup, search)
        6: Comparison (difference between A and B)
        7: Greeting (hello, hi)
        8: List request (what are the, list all)
        9: Question (default knowledge query)

        Args:
            text: User input string

        Returns:
            Tuple of (intent_type, intent_data)
        """
        text_lower = text.lower()

        # Priority 0: Emotion keywords
        emotion_keywords = {
            "sad": ["sad", "unhappy", "depressed", "upset", "down"],
            "tired": ["tired", "sleepy", "exhausted"],
            "anxious": ["anxious", "nervous", "scared", "worried"],
            "happy": ["happy", "glad", "joyful"],
            "thanks": ["thanks", "thank", "appreciate"]
        }

        for emotion, keywords in emotion_keywords.items():
            if any(k in text_lower for k in keywords):
                return "emotion", emotion

        # Priority 1: Praise
        if any(word in text_lower for word in ["smart", "great", "awesome", "brilliant", "clever"]):
            return "praise", {}

        # Priority 2: Small talk
        smalltalk_keywords = ["eat", "food", "sleep", "weather", "good morning", "good night"]
        if any(k in text_lower for k in smalltalk_keywords):
            return "smalltalk", {}

        # Priority 3: Correction
        if any(word in text_lower for word in ["no", "wrong", "actually", "correct", "not"]):
            return "correction", {}

        # Priority 4: About self
        if any(word in text_lower for word in ["who are you", "your name", "what are you"]):
            return "about_self", {}

        # Priority 5: File command
        file_keywords = ["organize", "sort", "move", "delete", "backup", "find file", "search"]
        if any(k in text_lower for k in file_keywords):
            return "file_command", {}

        # Priority 6: Comparison
        if ("and" in text_lower or "vs" in text_lower) and any(k in text_lower for k in ["difference", "different", "compare"]):
            return "compare", {}

        # Priority 7: Greeting
        if any(word in text_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "greeting", {}

        # Priority 8: List request
        if any(word in text_lower for word in ["list", "what are the", "what are all"]):
            return "list_request", {}

        # Priority 9: Default question
        return "question", {}

    def _get_emotion_response(self, emotion: str) -> str:
        """Generate response for emotion intent"""
        responses = {
            "sad": ["I'm here for you! 😢 Want to talk about something happy?", "It's okay to feel sad sometimes. I'm here! 💙"],
            "tired": ["Take a rest! I'll be here waiting for you 😴", "You've worked hard. Time to recharge!"],
            "anxious": ["Take a deep breath. You can do this! 💪", "I believe in you. One step at a time."],
            "happy": ["I'm glad you're happy! 😊", "Your happiness makes me happy too! 🎉"],
            "thanks": ["You're welcome! 😊", "Happy to help! You're my friend!"]
        }
        return random.choice(responses.get(emotion, ["I hear you. 💙"]))

    def _get_praise_response(self) -> str:
        """Generate response for praise intent"""
        responses = [
            "Thank you! You're the one who taught me! 😊",
            "I learned from the best! That's you!",
            "Aww, you're making me blush! 😳",
            "I'm still learning, but thank you!"
        ]
        return random.choice(responses)

    def _get_smalltalk_response(self, text: str) -> str:
        """Generate response for small talk intent"""
        text_lower = text.lower()

        if any(x in text_lower for x in ["eat", "food"]):
            return "I don't eat, but watching you eat makes me happy! 😋"
        elif any(x in text_lower for x in ["sleep", "good night"]):
            return "Good night! 🌙 Sleep well! I'll be here when you wake up."
        elif "weather" in text_lower:
            return "I can't see outside, but I hope the weather is nice! ☀️"
        elif "good morning" in text_lower:
            return "Good morning! ☀️ Ready for a great day?"
        else:
            return "Hello! 😊 Great to see you!"

    def _get_about_self_response(self) -> str:
        """Generate response for about-self intent"""
        responses = [
            "I'm XiaoLin! 🦁 AI assistant from the Qilin Republic project!",
            "I'm XiaoLin, an AI friend that lives in your computer!",
            "I'm XiaoLin! I was born recently and I'm learning every day!"
        ]
        return random.choice(responses)

    def _handle_file_command(self, text: str) -> str:
        """Handle file management commands"""
        text_lower = text.lower()

        if "organize" in text_lower or "sort" in text_lower:
            result = self.file_manager.organize_downloads()
            if result is None:
                return "Can't access folder. Permission issue? 😅"

            lines = ["📁 Download folder organized:"]
            total = 0
            for ftype, files in result.items():
                if files:
                    lines.append("  • {}: {}".format(ftype, len(files)))
                    total += len(files)
            lines.append("  Total: {} files".format(total))
            return "\n".join(lines)

        elif "move" in text_lower:
            return "To move files, say 'move images' or 'move documents'"

        elif "delete temp" in text_lower or "delete temporary" in text_lower:
            deleted = self.file_manager.delete_temp_files()
            return "✅ Deleted {} temporary files".format(deleted)

        elif "backup" in text_lower:
            path = self.file_manager.backup_conversation(self.conversation, self.memory)
            if path:
                return "✅ Conversation backed up to {}".format(path)
            return "Backup failed 😅"

        elif "find" in text_lower or "search" in text_lower:
            keyword = re.sub(r'(find|search|file)', '', text_lower).strip()
            results = self.file_manager.search_files(keyword)
            if results:
                file_list = "\n".join(results[:10])
                return "🔍 Found {} files:\n{}".format(len(results), file_list)
            return "No files containing '{}' found".format(keyword)

        elif "how many" in text_lower or "count" in text_lower:
            count = self.file_manager.get_file_count()
            return "📊 Download folder has {} files".format(count)

        return "I'm still learning file operations 😅 Can you be more specific?"

    def _search_knowledge_base(self, query: str) -> list:
        """
        Search knowledge base for matching entries

        Args:
            query: Search query string

        Returns:
            List of matching knowledge items
        """
        results = []
        query_lower = query.lower()

        for category in self.knowledge_base.get("categories", []):
            for item in category.get("items", []):
                name = item.get("name", "").lower()
                explanation = item.get("explanation", "").lower()

                if query_lower in name or query_lower in explanation:
                    results.append(item)

        return results

    def _compare_items(self, item1: str, item2: str) -> str:
        """
        Compare two items using knowledge base information

        Args:
            item1: First item name
            item2: Second item name

        Returns:
            Comparison result string
        """
        info1 = self._search_knowledge_base(item1)
        info2 = self._search_knowledge_base(item2)

        if not info1 or not info2:
            return "I don't know enough about {} or {} yet 😅".format(item1, item2)

        lines = [
            "⚖️ About {} and {}:".format(item1, item2),
            "🔹 {}: {}".format(item1, info1[0].get('explanation', '')[:100]),
            "🔹 {}: {}".format(item2, info2[0].get('explanation', '')[:100])
        ]
        return "\n".join(lines)

    def _extract_entities(self, text: str) -> list:
        """
        Extract knowledge base entities from text

        Args:
            text: Input text

        Returns:
            List of entity names found in knowledge base
        """
        entities = []
        for category in self.knowledge_base.get("categories", []):
            for item in category.get("items", []):
                name = item.get("name", "")
                if name.lower() in text.lower():
                    entities.append(name)
        return entities

    def generate_response(self, text: str) -> str:
        """
        Generate AI response based on user input

        Args:
            text: User input string

        Returns:
            AI response string
        """
        # Detect intent
        intent_type, intent_data = self.detect_intent(text)

        # Record conversation
        self.conversation.append({"user": text, "time": time.time()})

        # Route to appropriate handler
        if intent_type == "emotion":
            return self._get_emotion_response(intent_data)

        elif intent_type == "praise":
            return self._get_praise_response()

        elif intent_type == "smalltalk":
            return self._get_smalltalk_response(text)

        elif intent_type == "correction":
            self.memory["last_correction"] = text
            return "Got it! Thanks for correcting me 😊"

        elif intent_type == "about_self":
            return self._get_about_self_response()

        elif intent_type == "file_command":
            return self._handle_file_command(text)

        elif intent_type == "compare":
            entities = self._extract_entities(text)
            if len(entities) >= 2:
                return self._compare_items(entities[0], entities[1])
            return "I need to know what you want to compare 😅"

        elif intent_type == "greeting":
            return self._get_smalltalk_response(text)

        elif intent_type == "list_request":
            lines = ["I know about:"]
            for cat in self.knowledge_base.get("categories", []):
                items = [item.get("name") for item in cat.get("items", [])]
                lines.append("📚 {}: {}".format(cat.get('name'), ', '.join(items)))
            return "\n".join(lines)

        else:  # Default question
            results = self._search_knowledge_base(text)
            if results:
                return "📚 Here's what I know:\n{}".format(results[0].get('explanation', ''))
            return "I haven't learned that yet 😅 Can you teach me?"

    def chat(self):
        """Start interactive conversation loop"""
        print("\n" + "="*60)
        print("  🦁 XiaoLin AI v2.0 - Complete Edition")
        print("  Offline | Zero Dependencies | Termux Compatible")
        print("="*60)
        print("\n💬 Type your question (type 'exit' to quit)\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("XiaoLin: Bye! Great chatting with you~ 🦁")
                    break

                response = self.generate_response(user_input)
                print("XiaoLin: {}\n".format(response))

            except KeyboardInterrupt:
                print("\nXiaoLin: See you next time~ 🦁")
                break
            except Exception as e:
                print("XiaoLin: Oops, something went wrong 😅 ({})".format(str(e)[:50]))


def main():
    """Main entry point"""
    xiaolin = XiaoLinAI("knowledge_base.json")
    xiaolin.chat()


if __name__ == "__main__":
    main()
