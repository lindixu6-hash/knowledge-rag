<div align="center">

# 📚 Local Knowledge Base RAG System

[![GitHub Stars](https://img.shields.io/github/stars/lindixu6-hash/knowledge-rag?style=social)](https://github.com/lindixu6-hash/knowledge-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green)](https://ollama.com)
[![Milvus](https://img.shields.io/badge/Milvus-Vector%20DB-orange)](https://milvus.io)

**A privacy-first RAG (Retrieval-Augmented Generation) application running entirely on your local machine.**

Upload documents → Build vector embeddings → Chat with your knowledge base.

[English](#english) | [简体中文](#中文)

</div>

---

## English

### ✨ Features

- 🔒 **100% Local**: All data stays on your machine, no cloud API calls
- 📄 **Multiple Formats**: Support for `.md` and `.txt` documents
- 🧠 **Smart Chunking**: Configurable document splitting for better retrieval
- 🔍 **Vector Search**: Powered by Milvus vector database
- 🤖 **Local LLM**: Uses Ollama for embeddings and chat (no API costs!)
- 🎨 **Clean UI**: Simple web interface for easy interaction
- 📊 **Status Monitor**: Real-time system status and document tracking

### 🚀 Quick Start

```bash
# 1. Install Ollama (macOS)
brew install ollama
ollama serve

# 2. Pull models
ollama pull nomic-embed-text    # Embedding model
ollama pull gemma3:1b           # Chat model

# 3. Install Milvus Lite
pip install milvus-lite

# 4. Clone and run
git clone https://github.com/lindixu6-hash/knowledge-rag.git
cd knowledge-rag
pip install -r requirements.txt
python app.py
```

Open browser: **http://localhost:5000**

### 📸 Screenshot

> Upload your screenshot here! (Run the app and take a screenshot)

### 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask |
| LLM | Ollama (gemma3:1b) |
| Embeddings | Ollama (nomic-embed-text) |
| Vector DB | Milvus Lite |
| Frontend | Vanilla JS + CSS |

### 📖 Usage

1. **Upload Documents**: Add `.md` or `.txt` files to build your knowledge base
2. **Ask Questions**: Query your documents with natural language
3. **Get Answers**: AI retrieves relevant context and generates responses

---

## 中文

### ✨ 功能特性

- 🔒 **完全本地**：所有数据都在本地，绝不上云，隐私零泄露
- 📄 **多格式支持**：支持 `.md` 和 `.txt` 文档上传
- 🧠 **智能分段**：可配置的分块策略，提升检索效果
- 🔍 **向量检索**：基于 Milvus 向量数据库的高效搜索
- 🤖 **本地大模型**：使用 Ollama，无需 API 费用
- 🎨 **简洁界面**：开箱即用的 Web 界面
- 📊 **状态监控**：实时查看系统状态和文档列表

### 🚀 快速开始

```bash
# 1. 安装 Ollama (macOS)
brew install ollama
ollama serve

# 2. 拉取模型
ollama pull nomic-embed-text    # 向量模型
ollama pull gemma3:1b           # 问答模型

# 3. 安装 Milvus Lite
pip install milvus-lite

# 4. 克隆并运行
git clone https://github.com/lindixu6-hash/knowledge-rag.git
cd knowledge-rag
pip install -r requirements.txt
python app.py
```

打开浏览器访问：**http://localhost:5000**

### 📸 界面预览

> 这里放你的截图！（运行程序后截图替换）

### 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Flask |
| 大模型 | Ollama (gemma3:1b) |
| 向量模型 | Ollama (nomic-embed-text) |
| 向量数据库 | Milvus Lite |
| 前端 | 原生 JavaScript + CSS |

### 📖 使用流程

1. **上传文档**：将 `.md` 或 `.txt` 文件上传到知识库
2. **智能问答**：用自然语言提问
3. **获取答案**：AI 检索相关内容并生成回答

### ⚙️ 环境变量

```bash
# Ollama 服务地址
export OLLAMA_BASE_URL="http://localhost:11434"

# 向量模型
export EMBEDDING_MODEL="nomic-embed-text"

# 问答模型
export CHAT_MODEL="gemma3:1b"

# Milvus 配置
export MILVUS_HOST="localhost"
export MILVUS_PORT="19530"
```

### 🔧 故障排查

**Ollama 连接失败**
```bash
curl http://localhost:11434/api/tags
ollama serve
```

**模型未找到**
```bash
ollama list
ollama pull nomic-embed-text
ollama pull gemma3:1b
```

### 📄 License

[MIT License](LICENSE)

---

<div align="center">

**⭐ If this project helped you, please consider giving it a star!**

Made with ❤️ by [lindixu6-hash](https://github.com/lindixu6-hash)

</div>
