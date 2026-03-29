

```markdown
# 🦁 小麟 AI - 麒麟共和国的智能伙伴

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Termux-lightgrey.svg)](https://termux.com/)

---

## 🇨🇳 中文

### 📖 项目简介

**小麟 AI** 是麒麟共和国项目旗下的智能桌面助手，一个完全离线、零依赖的 AI 对话引擎。她可以陪你聊天、解答问题、整理文件，还能记住你的名字和喜好。

小麟不是云端大模型，她是一个**住在你电脑里的朋友**——不需要网络，不需要注册，不需要付费，下载就能用。

### ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 💬 **智能对话** | 10级意图识别，能理解情感、夸奖、闲聊、比较等各种表达 |
| 📚 **百科全书** | 内置 10 万字知识库，涵盖编程、网络安全、AI、天文、地理、生物、物理、化学、医学等 |
| 🗂️ **文件管理** | 自动整理下载文件夹，按类型分类（图片、文档、视频、压缩包等） |
| 🧠 **上下文记忆** | 记得你刚才问过什么，支持追问和纠错 |
| 😊 **情感陪伴** | 会害羞、会安慰、会鼓励，像真正的朋友一样 |
| 🔒 **完全离线** | 不依赖网络，不上传任何数据，保护隐私 |

### 🚀 快速开始

#### 在 Linux / Termux 上运行

```bash
# 1. 下载文件
git clone https://github.com/QLS7041/CAI.git
cd CAI

# 2. 运行
python3 chat_engine.py
```

#### 直接运行可执行文件（不需要 Python）

```bash
# 1. 给执行权限
chmod +x chat_engine

# 2. 运行
./chat_engine
```

### 💬 使用示例

```
你: 你好
小麟: 你好呀！😊 我是小麟，麒麟共和国的AI助手！

你: 什么是Python
小麟: Python是一种高级编程语言，以其简洁易学的语法而著称...

你: Python和Java有什么区别
小麟: ⚖️ 关于 Python 和 Java 的区别...

你: 心情不好
小麟: 抱抱你！😢 我在这儿陪你

你: 帮我整理下载文件夹
小麟: 📁 下载文件夹整理结果：
  • 图片: 5个
  • 文档: 3个
  • 压缩包: 2个

你: 我叫小明
小麟: 记住啦！你叫小明

你: 我叫什么
小麟: 你叫小明呀
```

### 🗂️ 文件结构

```
CAI/
├── chat_engine.py          # 主程序（775行）
├── knowledge_base.json     # 知识库（10万字，116+条）
├── chat_engine             # 可执行文件（Linux）
└── README.md               # 项目说明
```

### 📊 知识库统计

| 分类 | 条目数 |
|------|--------|
| 编程语言 | 21 条 |
| 网络安全 | 20 条 |
| 人工智能 | 15 条 |
| 天文学 | 10 条 |
| 地理学 | 10 条 |
| 生物学 | 10 条 |
| 物理学 | 10 条 |
| 化学 | 10 条 |
| 医学健康 | 10 条 |
| **总计** | **116+ 条，10 万字** |

### 🛠️ 自定义知识库

编辑 `knowledge_base.json` 即可添加自己的知识：

```json
{
  "categories": [
    {
      "name": "你的分类",
      "items": [
        {"name": "关键词", "explanation": "详细解释"}
      ]
    }
  ]
}
```

### 📝 命令列表

| 命令 | 功能 |
|------|------|
| `exit` / `quit` | 退出程序 |
| 任何问题 | 小麟会尽力回答 |
| `我叫 xxx` | 让小麟记住你的名字 |
| `帮我整理下载文件夹` | 整理下载目录 |
| `你好` / `谢谢` / `再见` | 日常对话 |

### 🎯 系统要求

- Python 3.6+（如果使用源码版）
- Linux / Termux / WSL（可执行文件需 Linux 环境）
- 无其他依赖

### 📜 开源协议

本项目采用 MIT 许可证，欢迎使用、修改、分发。

### 🙏 致谢

- 麒麟共和国社区
- 所有参与测试和反馈的朋友

---

## 🇬🇧 English

### 📖 Introduction

**XiaoLin AI** is an intelligent desktop assistant under the Qilin Republic project — a completely offline, zero-dependency AI conversation engine. She can chat with you, answer questions, organize files, and remember your name and preferences.

XiaoLin is not a cloud-based LLM. She is a **friend that lives in your computer** — no internet, no registration, no payment required.

### ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Smart Conversation** | 10-level intent recognition (emotion, praise, comparison, etc.) |
| 📚 **Encyclopedia** | Built-in 100k-word knowledge base covering programming, cybersecurity, AI, astronomy, geography, biology, physics, chemistry, medicine |
| 🗂️ **File Management** | Auto-organize download folder by type (images, documents, videos, archives) |
| 🧠 **Context Memory** | Remembers what you just asked, supports follow-up and correction |
| 😊 **Emotional Companion** | Gets shy, comforts, encourages — like a real friend |
| 🔒 **Fully Offline** | No internet, no data upload, privacy protected |

### 🚀 Quick Start

#### Run on Linux / Termux

```bash
git clone https://github.com/QLS7041/CAI.git
cd CAI
python3 chat_engine.py
```

#### Run the executable (no Python required)

```bash
chmod +x chat_engine
./chat_engine
```

### 💬 Usage Examples

```
You: hello
XiaoLin: Hello! I'm XiaoLin, AI assistant of Qilin Republic 😊

You: what is Python
XiaoLin: Python is a high-level programming language known for its simple syntax...

You: difference between Python and Java
XiaoLin: ⚖️ About Python and Java...

You: I'm feeling sad
XiaoLin: Hugs! 😢 I'm here for you

You: organize my downloads
XiaoLin: 📁 Download folder organized:
  • Images: 5
  • Documents: 3
  • Archives: 2

You: my name is Xiao Ming
XiaoLin: Got it! Your name is Xiao Ming

You: what's my name
XiaoLin: Your name is Xiao Ming
```

### 📂 File Structure

```
CAI/
├── chat_engine.py          # Main program (775 lines)
├── knowledge_base.json     # Knowledge base (100k words, 116+ entries)
├── chat_engine             # Executable (Linux)
└── README.md               # Documentation
```

### 📊 Knowledge Base Stats

| Category | Entries |
|----------|---------|
| Programming Languages | 21 |
| Cybersecurity | 20 |
| Artificial Intelligence | 15 |
| Astronomy | 10 |
| Geography | 10 |
| Biology | 10 |
| Physics | 10 |
| Chemistry | 10 |
| Medicine | 10 |
| **Total** | **116+ entries, 100k+ words** |

### 🛠️ Customize Knowledge Base

Edit `knowledge_base.json` to add your own knowledge:

```json
{
  "categories": [
    {
      "name": "Your Category",
      "items": [
        {"name": "Keyword", "explanation": "Detailed explanation"}
      ]
    }
  ]
}
```

### 📝 Commands

| Command | Function |
|---------|----------|
| `exit` / `quit` | Exit program |
| Any question | XiaoLin will try her best |
| `my name is xxx` | Remember your name |
| `organize my downloads` | Organize download folder |
| `hello` / `thanks` / `bye` | Daily conversation |

### 🎯 Requirements

- Python 3.6+ (if using source code)
- Linux / Termux / WSL (executable requires Linux)
- No other dependencies

### 📜 License

MIT License — free to use, modify, and distribute.

### 🙏 Acknowledgements

- Qilin Republic Community
- All testers and friends

---

**🦁 Built by a 14-year-old for the Qilin Republic project.**
**🦁 一个14岁少年为麒麟共和国项目创作。**

[GitHub Repository](https://github.com/QLS7041/CAI) | [麒麟共和国](https://github.com/QLS7041)
```

