# 本地知识库问答系统

基于 Ollama + Milvus 的 RAG（检索增强生成）应用，完全本地部署，保护隐私。

## 功能特性

- ✅ 支持 `.md` 和 `.txt` 格式文档上传
- ✅ 自动文档分段（可配置分段大小和分隔符）
- ✅ 使用本地 Ollama 向量模型进行文本嵌入
- ✅ 使用本地 Milvus 向量数据库存储和检索
- ✅ 基于本地 Ollama 模型进行智能问答
- ✅ 查看所有已嵌入的文档数据
- ✅ 实时系统状态监控

## 系统要求

### 已部署的模型和数据库

- Ollama 向量模型: `Qwen3-Embedding-0.6B:latest` 或 `nomic-embed-text:latest`
- Ollama 问答模型: `gemma3:1b`
- Milvus 向量数据库

**注意**: 系统支持自动检测，如果 `Qwen3-Embedding-0.6B` 未安装，会自动使用 `nomic-embed-text` 等其他可用模型。

### 安装前置依赖

1. **安装 Ollama**（如果还没有）
   ```bash
   # macOS
   brew install ollama

   # 启动 Ollama 服务
   ollama serve
   ```

2. **拉取模型**（如果还没有）
   ```bash
   # 向量模型（二选一或都安装）
   ollama pull nomic-embed-text:latest    # 768维，推荐
   ollama pull Qwen3-Embedding-0.6B:latest  # 如果需要使用此模型

   # 问答模型
   ollama pull gemma3:1b
   ```

3. **安装 Milvus**
   ```bash
   # 使用 Milvus Lite（推荐，无需 Docker）
   pip install milvus-lite

   # 或者使用 Docker 运行完整版 Milvus
   docker run -d --name milvus-standalone \
     -p 19530:19530 \
     -p 9091:9091 \
     milvusdb/milvus:latest
   ```

## 快速开始

### 1. 安装 Python 依赖

```bash
cd ~/knowledge-base-qa
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python app.py
```

### 3. 访问应用

打开浏览器访问: http://localhost:5000

## 目录结构

```
knowledge-base-qa/
├── app.py              # Flask 后端主文件
├── requirements.txt    # Python 依赖
├── README.md          # 说明文档
├── start.sh           # 启动脚本
├── static/
│   ├── css/
│   │   └── style.css   # 样式文件
│   └── js/
│       └── app.js      # 前端 JavaScript
├── templates/
│   └── index.html      # HTML 模板
└── uploads/            # 临时文件存储
```

## API 接口

### 获取系统状态
```
GET /api/status
```

### 上传文档
```
POST /api/upload
Content-Type: multipart/form-data

参数:
- file: 文件
- chunk_size: 分块大小（可选，默认 1024）
- separator: 分隔符（可选，默认 \n）
```

### 问答
```
POST /api/query
Content-Type: application/json

{
  "question": "问题文本",
  "top_k": 5
}
```

### 获取所有文档
```
GET /api/documents?limit=100
```

### 清空知识库
```
POST /api/clear
```

## 配置说明

### 环境变量

可通过环境变量自定义配置：

```bash
# Ollama 服务地址
export OLLAMA_BASE_URL="http://localhost:11434"

# 向量模型名称
export EMBEDDING_MODEL="Qwen3-Embedding-0.6B:latest"

# 问答模型名称
export CHAT_MODEL="gemma3:1b"

# Milvus 地址
export MILVUS_HOST="localhost"
export MILVUS_PORT="19530"
```

## 使用流程

1. **上传文档**
   - 点击「选择文件」上传 .md 或 .txt 文件
   - 调整分块大小和分隔符（可选）
   - 点击「上传并处理」

2. **智能问答**
   - 在输入框中输入问题
   - 选择检索文档数量
   - 点击「提问」查看答案

3. **管理文档**
   - 点击「查看所有文档」浏览已上传的内容
   - 点击「清空知识库」删除所有数据

## 参考资源

- [Ollama 官方文档](https://docs.ollama.com/capabilities/embeddings)
- [Milvus 官方文档](https://milvus.io/docs/quickstart.md)
- [PyMilvus GitHub](https://github.com/milvus-io/pymilvus)

## 故障排查

### Ollama 连接失败
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 重启 Ollama
ollama serve
```

### Milvus 连接失败
```bash
# 如果使用 Docker，检查容器状态
docker ps | grep milvus

# 查看日志
docker logs milvus-standalone
```

### 模型未找到
```bash
# 检查已安装的模型
ollama list

# 重新拉取模型
ollama pull Qwen3-Embedding-0.6B:latest
ollama pull gemma3:1b
```

## 许可证

MIT License
