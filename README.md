# Knowledge RAG

一个强调隐私、本地部署和低成本运行的知识库 RAG 原型。

这个项目解决的不是“怎么再做一个聊天框”，而是一个更实际的问题：

> 当用户希望把自己的文档变成可检索、可追问、不会上云泄露的本地知识助手时，怎样把上传、分块、嵌入、检索、生成和管理串成一个可运行的产品闭环。

[![GitHub Stars](https://img.shields.io/github/stars/lindixu6-hash/knowledge-rag?style=social)](https://github.com/lindixu6-hash/knowledge-rag)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green)](https://ollama.com)
[![Milvus](https://img.shields.io/badge/Milvus-Vector%20DB-orange)](https://milvus.io)

## 项目定位

如果把这个仓库当成求职作品，它更适合被理解为一个：

- **本地 AI 应用原型**
- **RAG 系统最小可用产品**
- **隐私优先的知识库问答工具**

它体现的重点不是“模型调得多大”，而是：

- 是否理解真实用户为什么会需要本地 RAG
- 是否能把 RAG 系统拆成清晰的产品流程和工程模块
- 是否能把“隐私、成本、部署门槛、可用性”一起纳入设计

## 我想解决的问题

很多知识库问答产品默认依赖云端 API，但真实用户经常会卡在这几件事上：

1. 文档里有隐私，不想上传到第三方平台
2. 想低成本试用，不想先配一堆 API Key
3. 想把自己的笔记、学习资料、项目文档快速变成可问答系统
4. 想看一个真正能跑的本地 AI 工作流，而不是概念 demo

所以这个项目选择了一条很明确的路线：

- **模型本地化**：Ollama
- **向量检索本地化**：Milvus Lite
- **应用形态轻量化**：Flask + 原生前端

## 核心方案

### 1. 本地优先架构

整个流程都可以在本机完成：

- 上传文档
- 文本分块
- 向量嵌入
- 向量检索
- 生成回答

这意味着它天然适合：

- 个人知识库
- 学习资料问答
- 本地项目文档检索
- 对隐私更敏感的使用场景

### 2. 模型自动检测与降级

项目不是写死某一个模型，而是会自动检测本地 Ollama 可用模型。

当前支持的方向包括：

- embedding: `qwen3-embedding:0.6b` / `nomic-embed-text` / `mxbai-embed-large`
- chat: `gemma3:1b` / `qwen2.5:0.5b` / `llama3.2:1b` / `phi3:mini`

这能明显降低“环境刚搭好但模型名不匹配就跑不起来”的挫败感。

### 3. 可配置分块策略

上传文档后，系统会按配置进行文本切分。

这件事虽然听起来工程化，但其实很有产品意义：

- 分块太大，召回不准
- 分块太小，语义不完整
- 分隔符不对，知识结构会被切碎

项目里把这些参数暴露出来，方便后续继续调优。

### 4. 知识库管理闭环

不只是“能问答”，还包括最基本的知识库管理能力：

- 查看系统状态
- 上传文档
- 查看文档列表
- 清空知识库
- 查询结果返回来源片段

这让它更像一个完整原型，而不是一次性的脚本。

## 这个项目体现的能力

如果你拿这个项目投 AI PM / AI 应用产品 / AI 工具产品岗位，它比较能体现：

- **RAG 理解能力**  
  理解上传、切分、嵌入、召回、生成的完整链路

- **场景抽象能力**  
  从“我想问本地文档”抽象到一套可交互的知识库产品

- **产品权衡能力**  
  在隐私、成本、精度、部署复杂度之间做取舍

- **工程协同能力**  
  能把 Flask、Ollama、Milvus Lite 和前端交互组织成可运行系统

- **本地 AI 落地意识**  
  不只关注模型能力，也关注本地部署体验和实际可用性

## 用户流程

```text
上传文档
  ↓
文本分块
  ↓
生成向量嵌入
  ↓
写入 Milvus Lite
  ↓
用户提问
  ↓
向量召回相关片段
  ↓
Ollama 生成回答
  ↓
返回答案 + 来源
```

## 核心功能

### 用户侧

- 支持上传 `.md` / `.txt` 文档
- 通过 Web 页面直接问答
- 返回基于知识库的回答
- 查看文档列表与系统状态

### 系统侧

- 本地模型自动检测
- 文本分块与向量化
- Milvus Lite 本地向量检索
- 本地聊天模型生成回答
- 基础测试脚本与启动脚本

## 技术栈

| 模块 | 技术 |
|------|------|
| 后端 | Flask |
| 本地模型 | Ollama |
| 向量数据库 | Milvus Lite |
| 检索生成 | 本地 Embedding + Chat Model |
| 前端 | Vanilla JS + CSS |
| 测试 | Python 测试脚本 |

## 关键代码入口

- 应用入口: [app.py](app.py)
- 前端页面: [templates/index.html](templates/index.html)
- 前端交互: [static/js/app.js](static/js/app.js)
- 启动脚本: [start.sh](start.sh)
- 测试脚本: [test_app.py](test_app.py)

## 主要接口

- `GET /api/status`  
  查看 Ollama、Milvus、模型和知识库状态

- `POST /api/upload`  
  上传文档并写入知识库

- `POST /api/query`  
  基于知识库问答

- `GET /api/documents`  
  获取当前文档列表

- `POST /api/clear`  
  清空知识库

## 目录结构

```text
knowledge-rag/
├── app.py
├── start.sh
├── requirements.txt
├── templates/
├── static/
├── test_app.py
└── README.md
```

## 快速开始

### 1. 准备 Ollama

```bash
brew install ollama
ollama serve
```

### 2. 拉取本地模型

```bash
ollama pull nomic-embed-text
ollama pull gemma3:1b
```

如果你本地已经有其他兼容模型，系统也会优先自动检测。

### 3. 安装依赖

```bash
git clone https://github.com/lindixu6-hash/knowledge-rag.git
cd knowledge-rag
pip install -r requirements.txt
```

### 4. 启动

推荐直接运行：

```bash
bash start.sh
```

或手动运行：

```bash
python3 app.py
```

默认访问地址：

- `http://localhost:5001`

## 环境变量

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
export EMBEDDING_MODEL="nomic-embed-text"
export CHAT_MODEL="gemma3:1b"
export MILVUS_HOST="localhost"
export MILVUS_PORT="19530"
```

## 适合在面试里怎么讲

这个项目比较适合从下面几个角度展开：

1. 为什么本地 RAG 对一部分用户比云端 RAG 更有吸引力
2. 为什么模型自动检测和低门槛部署，对产品体验很关键
3. 为什么 RAG 的效果不只取决于模型，还取决于切分和召回策略
4. 为什么这个项目适合做“隐私优先 AI 工具”的最小闭环
5. 如果继续迭代，怎样增加文档类型、召回评测和来源可视化

## 可以继续优化的方向

- 支持 PDF、DOCX 等更多文档格式
- 增加召回结果可视化与 chunk 调试视图
- 支持多知识库、多标签管理
- 增加引用高亮与来源定位
- 增加 answer quality eval 和检索质量评估

## 说明

这个项目强调本地运行，所以没有放公网在线 demo。  
它更适合通过本地演示、录屏或截图来展示。

## License

MIT
