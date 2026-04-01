
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小麟 AI 对话引擎 v2.0 完整版
================================

一个完全离线、零依赖的智能对话引擎，包含：
- 10级意图优先级系统
- 文件管理模块
- 情感识别
- 上下文记忆

麒麟共和国项目 | Termux兼容 | MIT许可证
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
    """文件管理模块 - 处理文件的整理、移动、删除、搜索等操作"""

    def __init__(self):
        """初始化文件管理器，设置默认的Android存储路径"""
        self.download_dir = "/storage/emulated/0/Download"
        self.pictures_dir = "/storage/emulated/0/Pictures"
        self.documents_dir = "/storage/emulated/0/Documents"
        self.backup_dir = "/storage/emulated/0/qlsf/backup"

        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)

    def get_file_type(self, filename: str) -> str:
        """
        根据文件扩展名判断文件类型

        参数:
            filename: 文件名

        返回:
            文件类型分类 (image/document/video/archive/temp/other)
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
        按文件类型整理下载文件夹

        返回:
            以文件类型为键、文件列表为值的字典
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
        将指定类型的所有文件移动到目标目录

        参数:
            file_type: 要移动的文件类型
            target_dir: 目标目录路径

        返回:
            成功移动的文件数量
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
        删除下载文件夹中的所有临时文件

        返回:
            删除的文件数量
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
        搜索文件名中包含关键词的文件

        参数:
            keyword: 搜索关键词

        返回:
            匹配的文件名列表
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
        获取下载文件夹中的文件总数

        返回:
            文件数量
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
        删除指定的文件

        参数:
            filename: 要删除的文件名

        返回:
            成功返回True，失败返回False
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
        备份对话历史到JSON文件

        参数:
            conversation: 对话记录列表
            memory: 用户记忆字典

        返回:
            备份文件路径，失败返回None
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
    """小麟 AI 对话引擎 - 核心对话类"""

    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        """
        初始化小麟AI

        参数:
            knowledge_base_path: 知识库JSON文件路径
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

        # AI人设
        self.personality = {
            "name": "小麟",
            "emoji": "🦁",
            "age": "刚出生不久",
            "origin": "麒麟共和国"
        }

    def _load_knowledge_base(self) -> dict:
        """
        从JSON文件加载知识库

        返回:
            知识库字典，文件不存在则返回空结构
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
        10级意图优先级检测系统

        优先级顺序（0最高，9最低）:
        0: 情感 (难过、累、焦虑、开心、感谢)
        1: 表扬 (聪明、厉害、棒)
        2: 闲聊 (吃饭、睡觉、天气、问候)
        3: 纠错 (不对、错了、其实是)
        4: 关于自己 (你是谁、你叫什么)
        5: 文件命令 (整理、删除、备份、搜索)
        6: 比较 (A和B的区别)
        7: 打招呼 (你好、嗨)
        8: 列表请求 (有哪些、列举)
        9: 普通问答

        参数:
            text: 用户输入字符串

        返回:
            (意图类型, 意图数据) 元组
        """
        text_lower = text.lower()

        # 优先级0: 情感关键词
        emotion_keywords = {
            "sad": ["难过", "伤心", "郁闷", "心情不好"],
            "tired": ["累", "困", "疲惫", "累死了"],
            "anxious": ["焦虑", "紧张", "害怕", "恐惧"],
            "happy": ["开心", "高兴", "哈哈", "嘻嘻"],
            "thanks": ["谢谢", "感谢", "谢了"]
        }

        for emotion, keywords in emotion_keywords.items():
            if any(k in text_lower for k in keywords):
                return "emotion", emotion

        # 优先级1: 表扬词
        if any(word in text_lower for word in ["聪明", "厉害", "棒", "你怎么这么", "太厉害"]):
            return "praise", {}

        # 优先级2: 闲聊
        smalltalk_keywords = ["吃饭", "睡觉", "天气", "早上好", "晚安", "晚上好"]
        if any(k in text_lower for k in smalltalk_keywords):
            return "smalltalk", {}

        # 优先级3: 纠错
        if any(word in text_lower for word in ["不对", "错了", "我说的是", "其实是", "纠正"]):
            return "correction", {}

        # 优先级4: 关于自己
        if any(word in text_lower for word in ["你叫什么", "你是谁", "你多大", "你名字"]):
            return "about_self", {}

        # 优先级5: 文件命令
        file_keywords = ["整理", "分类", "移动", "删除", "备份", "找文件", "多少文件"]
        if any(k in text_lower for k in file_keywords):
            return "file_command", {}

        # 优先级6: 比较
        if ("和" in text_lower or "跟" in text_lower) and any(k in text_lower for k in ["区别", "不同", "哪个", "对比"]):
            return "compare", {}

        # 优先级7: 打招呼
        if any(word in text_lower for word in ["你好", "嗨", "hi", "hello"]):
            return "greeting", {}

        # 优先级8: 列表请求
        if any(word in text_lower for word in ["有哪些", "列举", "都有什么"]):
            return "list_request", {}

        # 优先级9: 默认问答
        return "question", {}

    def _get_emotion_response(self, emotion: str) -> str:
        """生成情感意图的回复"""
        responses = {
            "sad": ["抱抱你！😢 要不要聊点开心的事？", "心情不好的时候我陪你呢。💙"],
            "tired": ["累了就休息一会儿，我在这儿等你~ 😴", "辛苦啦！休息一下再继续吧"],
            "anxious": ["深呼吸，慢慢来，你可以的！💪", "我都相信你！"],
            "happy": ["太好了！你开心我也开心！🎉", "哈哈，看来今天是个好天气呢😊"],
            "thanks": ["客气啦！😊", "我们是好朋友嘛~"]
        }
        return random.choice(responses.get(emotion, ["我听到你的感受了~ 💙"]))

    def _get_praise_response(self) -> str:
        """生成表扬意图的回复"""
        responses = [
            "嘿嘿，是你教得好呀！😊",
            "跟你学的！你更聪明！",
            "被夸了！有点害羞呢😳",
            "我还在学习呢，谢谢你！"
        ]
        return random.choice(responses)

    def _get_smalltalk_response(self, text: str) -> str:
        """生成闲聊意图的回复"""
        text_lower = text.lower()

        if "吃饭" in text_lower:
            return "我不用吃饭，但看你吃得香我就开心！😋"
        elif "睡觉" in text_lower or "晚安" in text_lower:
            return "晚安！🌙 睡个好觉！"
        elif "天气" in text_lower:
            return "天气怎么样呀？我在电脑里看不到外面呢~"
        elif "早上好" in text_lower:
            return "早上好！☀️ 又是崭新的一天！"
        elif "晚上好" in text_lower:
            return "晚上好！🌙 今天过得怎么样？"
        else:
            return "你好呀！😊 很高兴见到你！"

    def _get_about_self_response(self) -> str:
        """生成关于自己的回复"""
        responses = [
            "我叫小麟！🦁 麒麟共和国的AI助手",
            "我是小麟，一个住在你电脑/手机里的AI朋友~",
            "我是小麟，刚出生不久，还在学习成长呢！"
        ]
        return random.choice(responses)

    def _handle_file_command(self, text: str) -> str:
        """处理文件管理命令"""
        text_lower = text.lower()

        if "整理" in text_lower or "分类" in text_lower:
            result = self.file_manager.organize_downloads()
            if result is None:
                return "文件夹访问失败，可能是权限问题 😅"

            lines = ["📁 下载文件夹整理结果："]
            total = 0
            for ftype, files in result.items():
                if files:
                    lines.append("  • {}: {}".format(ftype, len(files)))
                    total += len(files)
            lines.append("  总计: {}个文件".format(total))
            return "\n".join(lines)

        elif "删除临时" in text_lower:
            deleted = self.file_manager.delete_temp_files()
            return "✅ 已删除 {} 个临时文件".format(deleted)

        elif "备份" in text_lower:
            path = self.file_manager.backup_conversation(self.conversation, self.memory)
            if path:
                return "✅ 对话已备份到 {}".format(path)
            return "备份失败了呢 😅"

        elif "找" in text_lower and "文件" in text_lower:
            keyword = text_lower.replace("找", "").replace("文件", "").strip()
            results = self.file_manager.search_files(keyword)
            if results:
                file_list = "\n".join(results[:10])
                return "🔍 找到 {} 个文件：\n{}".format(len(results), file_list)
            return "没找到包含'{}'的文件".format(keyword)

        elif "多少" in text_lower and "文件" in text_lower:
            count = self.file_manager.get_file_count()
            return "📊 下载文件夹有 {} 个文件".format(count)

        return "这个文件操作我还在学呢~ 😅 能说得具体点吗？"

    def _search_knowledge_base(self, query: str) -> list:
        """
        在知识库中搜索匹配条目

        参数:
            query: 搜索查询字符串

        返回:
            匹配的知识条目列表
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
        使用知识库信息比较两个事物

        参数:
            item1: 第一个事物名称
            item2: 第二个事物名称

        返回:
            比较结果字符串
        """
        info1 = self._search_knowledge_base(item1)
        info2 = self._search_knowledge_base(item2)

        if not info1 or not info2:
            return "关于'{}'或'{}'的信息不够，我还在学习中 😅".format(item1, item2)

        lines = [
            "⚖️ 关于 {} 和 {}：".format(item1, item2),
            "🔹 {}：{}".format(item1, info1[0].get('explanation', '')[:100]),
            "🔹 {}：{}".format(item2, info2[0].get('explanation', '')[:100])
        ]
        return "\n".join(lines)

    def _extract_entities(self, text: str) -> list:
        """
        从文本中提取知识库中的实体名称

        参数:
            text: 输入文本

        返回:
            在知识库中找到的实体名称列表
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
        根据用户输入生成AI回复

        参数:
            text: 用户输入字符串

        返回:
            AI回复字符串
        """
        # 检测意图
        intent_type, intent_data = self.detect_intent(text)

        # 记录对话
        self.conversation.append({"user": text, "time": time.time()})

        # 路由到对应的处理器
        if intent_type == "emotion":
            return self._get_emotion_response(intent_data)

        elif intent_type == "praise":
            return self._get_praise_response()

        elif intent_type == "smalltalk":
            return self._get_smalltalk_response(text)

        elif intent_type == "correction":
            self.memory["last_correction"] = text
            return "好的，我记住了！谢谢你的纠正😊"

        elif intent_type == "about_self":
            return self._get_about_self_response()

        elif intent_type == "file_command":
            return self._handle_file_command(text)

        elif intent_type == "compare":
            entities = self._extract_entities(text)
            if len(entities) >= 2:
                return self._compare_items(entities[0], entities[1])
            return "我需要知道你要比较哪两个东西呢~ 😅"

        elif intent_type == "greeting":
            return self._get_smalltalk_response(text)

        elif intent_type == "list_request":
            lines = ["我知道的东西有："]
            for cat in self.knowledge_base.get("categories", []):
                items = [item.get("name") for item in cat.get("items", [])]
                lines.append("📚 {}：{}".format(cat.get('name'), ', '.join(items)))
            return "\n".join(lines)

        else:  # 默认问答
            results = self._search_knowledge_base(text)
            if results:
                return "📚 这个我来解答一下！\n{}".format(results[0].get('explanation', ''))
            return "这个我还没学过呢😅 你能教我吗？"

    def chat(self):
        """开始交互式对话"""
        print("\n" + "="*60)
        print("  🦁 小麟 AI v2.0 - 完整版")
        print("  离线 | 零依赖 | Termux兼容")
        print("="*60)
        print("\n💬 输入你的问题（输入 'exit' 退出）\n")

        while True:
            try:
                user_input = input("你: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', '退出', 'quit']:
                    print("小麟: 拜拜！很高兴和你聊天~ 🦁")
                    break

                response = self.generate_response(user_input)
                print("小麟: {}\n".format(response))

            except KeyboardInterrupt:
                print("\n小麟: 下次见~ 🦁")
                break
            except Exception as e:
                print("小麟: 出错了 😅 ({})".format(str(e)[:50]))


def main():
    """主函数入口"""
    xiaolin = XiaoLinAI("knowledge_base.json")
    xiaolin.chat()


if __name__ == "__main__":
    main()
