#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地知识库问答系统
基于 Ollama + Milvus 的 RAG 应用

作者: Claude Code
创建日期: 2026-05-06
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import requests
import numpy as np
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)

# ============================================================================
# 配置
# ============================================================================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 支持的嵌入模型列表（按优先级排序）
SUPPORTED_EMBEDDING_MODELS = [
    "qwen3-embedding:0.6b",
    "nomic-embed-text:latest",
    "mxbai-embed-large:latest",
    "all-minilm:latest",
]

SUPPORTED_CHAT_MODELS = [
    "gemma3:1b",
    "qwen2.5:0.5b",
    "qwen2.5-0.5b:latest",
    "llama3.2:1b",
    "phi3:mini",
]

# 默认模型（将在启动时自动检测）
EMBEDDING_MODEL = None
CHAT_MODEL = None

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = "knowledge_base"

# Milvus Lite ID 计数器
INSERT_ID_COUNTER = 0

# 默认分段配置
DEFAULT_CHUNK_SIZE = 1024  # 字符数
DEFAULT_CHUNK_SEPARATOR = "\n"  # 分隔符

# ============================================================================
# Flask 应用初始化
# ============================================================================

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置文件上传
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {".md", ".txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB 最大文件

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================================
# 模型自动检测
# ============================================================================


def detect_available_models() -> tuple:
    """
    自动检测 Ollama 中可用的模型

    Returns:
        (embedding_model, chat_model) 找到的模型，未找到则返回 (None, None)
    """
    global EMBEDDING_MODEL, CHAT_MODEL

    # 检查环境变量是否指定了模型
    env_embedding = os.getenv("EMBEDDING_MODEL")
    env_chat = os.getenv("CHAT_MODEL")

    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            available_models = [m.get("name", "") for m in data.get("models", [])]

            # 如果环境变量指定了模型，优先使用
            if env_embedding and env_embedding in available_models:
                EMBEDDING_MODEL = env_embedding
            else:
                # 自动检测嵌入模型
                for model in SUPPORTED_EMBEDDING_MODELS:
                    if model in available_models:
                        EMBEDDING_MODEL = model
                        break

            if env_chat and env_chat in available_models:
                CHAT_MODEL = env_chat
            else:
                # 自动检测聊天模型
                for model in SUPPORTED_CHAT_MODELS:
                    if model in available_models:
                        CHAT_MODEL = model
                        break

    except Exception as e:
        print(f"检测模型失败: {e}")

    return EMBEDDING_MODEL, CHAT_MODEL


# 启动时检测模型
detect_available_models()

# ============================================================================
# Milvus 连接管理
# ============================================================================


class MilvusManager:
    """Milvus 向量数据库管理器"""

    def __init__(self, host: str = MILVUS_HOST, port: str = MILVUS_PORT):
        self.host = host
        self.port = port
        self.connected = False
        self.collection: Optional[Collection] = None
        self._dimension = None  # 将在首次嵌入后自动检测

    def connect(self) -> bool:
        """连接到 Milvus 服务器"""
        try:
            # 先尝试使用 milvus-lite（内嵌模式）
            try:
                from pymilvus import MilvusClient

                self.client = MilvusClient("./milvus_data.db")
                self.use_lite = True
                print("使用 Milvus Lite 模式")
                self.connected = True
                return True
            except ImportError:
                pass

            # 回退到标准 Milvus 连接
            connections.connect(host=self.host, port=self.port)
            self.use_lite = False
            self.connected = True
            print(f"已连接到 Milvus: {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"连接 Milvus 失败: {e}")
            return False

    def get_dimension(self) -> int:
        """获取向量维度（通过测试嵌入获取）"""
        if self._dimension is not None:
            return self._dimension

        test_embedding = get_embedding("测试")
        if test_embedding:
            self._dimension = len(test_embedding)
            return self._dimension
        raise ValueError("无法获取向量维度")

    def create_collection(self, dimension: int) -> Collection:
        """创建集合"""
        if self.use_lite:
            # Milvus Lite 使用简单的集合创建方式
            if self.client.has_collection(COLLECTION_NAME):
                self.client.drop_collection(COLLECTION_NAME)

            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                dimension=dimension,
            )
            print(f"Milvus Lite: 集合 '{COLLECTION_NAME}' 创建成功")
            return None

        # 标准 Milvus 模式
        if utility.has_collection(COLLECTION_NAME):
            utility.drop_collection(COLLECTION_NAME)

        # 定义 Schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source_file", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
        ]

        schema = CollectionSchema(
            fields=fields,
            description="知识库文档向量集合",
            enable_dynamic_field=True,
        )

        collection = Collection(name=COLLECTION_NAME, schema=schema)
        collection.create_index(field_name="vector", index_params={"index_type": "IVF_FLAT", "metric_type": "COSINE", "params": {"nlist": 128}})

        print(f"集合 '{COLLECTION_NAME}' 创建成功，维度: {dimension}")
        self.collection = collection
        return collection

    def ensure_collection(self) -> bool:
        """确保集合存在（创建或获取）"""
        global INSERT_ID_COUNTER
        try:
            dimension = self.get_dimension()

            if self.use_lite:
                # 检查集合是否存在，如果存在但有错误，重新创建
                if self.client.has_collection(COLLECTION_NAME):
                    # 尝试查询，如果失败则重新创建
                    try:
                        self.client.query(COLLECTION_NAME, filter="id >= 0", limit=1)
                    except:
                        print("集合异常，重新创建...")
                        self.client.drop_collection(COLLECTION_NAME)
                        INSERT_ID_COUNTER = 0
                        self.client.create_collection(
                            collection_name=COLLECTION_NAME,
                            dimension=dimension,
                        )
                else:
                    self.client.create_collection(
                        collection_name=COLLECTION_NAME,
                        dimension=dimension,
                    )
                return True

            # 标准 Milvus 模式
            if utility.has_collection(COLLECTION_NAME):
                self.collection = Collection(COLLECTION_NAME)
                self.collection.load()
            else:
                self.create_collection(dimension)
            return True
        except Exception as e:
            print(f"确保集合存在失败: {e}")
            return False

    def insert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """插入文档分块和向量"""
        global INSERT_ID_COUNTER
        try:
            if self.use_lite:
                # Milvus Lite 模式
                data = []
                for chunk, embedding in zip(chunks, embeddings):
                    data.append({
                        "id": INSERT_ID_COUNTER,  # 使用全局计数器
                        "vector": embedding,
                        "text": chunk["text"],
                        "source_file": chunk["source_file"],
                        "chunk_index": chunk["chunk_index"],
                    })
                    INSERT_ID_COUNTER += 1
                self.client.insert(COLLECTION_NAME, data)
                return True

            # 标准 Milvus 模式
            if not self.collection:
                self.ensure_collection()

            data = [
                {
                    "text": chunk["text"],
                    "source_file": chunk["source_file"],
                    "chunk_index": chunk["chunk_index"],
                    "vector": embedding,
                }
                for chunk, embedding in zip(chunks, embeddings)
            ]

            self.collection.insert(data)
            self.collection.flush()
            return True
        except Exception as e:
            print(f"插入数据失败: {e}")
            return False

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """向量相似度搜索"""
        try:
            if self.use_lite:
                # Milvus Lite 模式
                results = self.client.search(
                    collection_name=COLLECTION_NAME,
                    data=[query_embedding],
                    limit=top_k,
                    output_fields=["text", "source_file", "chunk_index"],
                )
                return results[0]

            # 标准 Milvus 模式
            if not self.collection:
                self.ensure_collection()

            self.collection.load()

            results = self.collection.search(
                data=[query_embedding],
                anns_field="vector",
                param={"metric_type": "COSINE", "params": {"nprobe": 10}},
                limit=top_k,
                output_fields=["text", "source_file", "chunk_index"],
            )
            return results[0]
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def get_all_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取向量数据库中的所有数据"""
        try:
            if self.use_lite:
                # Milvus Lite 模式
                results = self.client.query(
                    collection_name=COLLECTION_NAME,
                    filter="",  # 空过滤条件表示获取所有数据
                    limit=limit,
                    output_fields=["text", "source_file", "chunk_index"],
                )
                return results

            # 标准 Milvus 模式
            if not self.collection:
                self.ensure_collection()

            self.collection.load()
            results = self.collection.query(
                expr="",  # 空表达式表示获取所有数据
                output_fields=["text", "source_file", "chunk_index"],
                limit=limit,
            )
            return results
        except Exception as e:
            print(f"获取所有数据失败: {e}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            if self.use_lite:
                # Milvus Lite 模式
                count = self.client.query(
                    collection_name=COLLECTION_NAME,
                    filter="id >= 0",
                    limit=1,
                )
                total_count = len(self.client.query(
                    collection_name=COLLECTION_NAME,
                    filter="",
                    limit=999999,
                ))
                return {
                    "name": COLLECTION_NAME,
                    "count": total_count,
                    "mode": "milvus-lite",
                }

            # 标准 Milvus 模式
            if not self.collection:
                self.ensure_collection()

            self.collection.load()
            stats = self.collection.describe()
            return {
                "name": COLLECTION_NAME,
                "count": self.collection.num_entities,
                "schema": stats,
            }
        except Exception as e:
            print(f"获取集合信息失败: {e}")
            return {}

    def clear_collection(self) -> bool:
        """清空集合"""
        try:
            if self.use_lite:
                self.client.drop_collection(COLLECTION_NAME)
                dimension = self.get_dimension()
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    dimension=dimension,
                )
                return True

            # 标准 Milvus 模式
            if utility.has_collection(COLLECTION_NAME):
                utility.drop_collection(COLLECTION_NAME)
            self.ensure_collection()
            return True
        except Exception as e:
            print(f"清空集合失败: {e}")
            return False


# 全局 Milvus 管理器实例
milvus_manager = MilvusManager()

# ============================================================================
# Ollama API 调用
# ============================================================================


def get_embedding(text: str) -> Optional[List[float]]:
    """
    调用 Ollama API 获取文本向量嵌入

    Args:
        text: 输入文本

    Returns:
        向量列表，失败返回 None
    """
    try:
        # 尝试两种 API 格式
        for endpoint in ["/api/embeddings", "/api/embed"]:
            response = requests.post(
                f"{OLLAMA_BASE_URL}{endpoint}",
                json={"model": EMBEDDING_MODEL, "prompt": text},
                timeout=30,
            )
            if response.status_code == 200:
                result = response.json()
                # 不同版本的 Ollama 返回格式不同
                if "embedding" in result:
                    return result["embedding"]
                elif "embeddings" in result:
                    return result["embeddings"][0]

        print(f"获取嵌入失败: {response.text}")
        return None
    except Exception as e:
        print(f"调用 Ollama Embedding API 失败: {e}")
        return None


def chat_completion(messages: List[Dict[str, str]], stream: bool = False) -> str:
    """
    调用 Ollama API 进行对话

    Args:
        messages: 对话消息列表
        stream: 是否流式输出

    Returns:
        模型回复文本
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": CHAT_MODEL, "messages": messages, "stream": stream},
            timeout=60,
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("message", {}).get("content", "")

        print(f"Chat API 调用失败: {response.text}")
        return ""
    except Exception as e:
        print(f"调用 Ollama Chat API 失败: {e}")
        return ""


# ============================================================================
# 文档处理
# ============================================================================


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def split_text(content: str, chunk_size: int = DEFAULT_CHUNK_SIZE, separator: str = DEFAULT_CHUNK_SEPARATOR) -> List[str]:
    """
    分割文本为多个块

    Args:
        content: 原始文本内容
        chunk_size: 每块最大字符数
        separator: 分隔符

    Returns:
        文本块列表
    """
    # 先按分隔符分割
    segments = content.split(separator)

    chunks = []
    current_chunk = ""

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        # 如果当前块加上新段落超过限制，先保存当前块
        if len(current_chunk) + len(segment) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = segment
        else:
            if current_chunk:
                current_chunk += separator + segment
            else:
                current_chunk = segment

    # 添加最后一个块
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def parse_file(file_path: str, filename: str) -> List[Dict[str, Any]]:
    """
    解析文件并分块

    Args:
        file_path: 文件路径
        filename: 文件名

    Returns:
        分块信息列表
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = split_text(content)

    result = []
    for i, chunk_text in enumerate(chunks):
        result.append({
            "text": chunk_text,
            "source_file": filename,
            "chunk_index": i,
        })

    return result


# ============================================================================
# Web 路由
# ============================================================================


@app.route("/")
def index():
    """主页"""
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    """获取系统状态"""
    # 检查 Ollama 连接
    ollama_status = {"connected": False, "models": []}
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            ollama_status["connected"] = True
            ollama_status["models"] = [m.get("name", "") for m in models]
    except Exception as e:
        ollama_status["error"] = str(e)

    # 检查 Milvus 连接
    milvus_status = {"connected": milvus_manager.connected}
    if milvus_manager.connected:
        try:
            milvus_status.update(milvus_manager.get_collection_info())
        except Exception as e:
            milvus_status["error"] = str(e)

    return jsonify({
        "ollama": ollama_status,
        "milvus": milvus_status,
        "embedding_model": EMBEDDING_MODEL,
        "chat_model": CHAT_MODEL,
    })


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """
    上传文档并处理

    参数:
        file: 上传的文件
        chunk_size: 分块大小（可选，默认 1024）
        separator: 分隔符（可选，默认换行符）
    """
    # 确保 Milvus 集合存在
    if not milvus_manager.ensure_collection():
        return jsonify({"error": "Milvus 集合初始化失败"}), 500

    if "file" not in request.files:
        return jsonify({"error": "没有上传文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "文件名为空"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件格式，仅支持 .md 和 .txt"}), 400

    # 获取分块参数
    chunk_size = int(request.form.get("chunk_size", DEFAULT_CHUNK_SIZE))
    separator = request.form.get("separator", DEFAULT_CHUNK_SEPARATOR)

    # 保存文件
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    # 解析文件
    chunks = parse_file(file_path, file.filename)

    if not chunks:
        return jsonify({"error": "文件解析失败或内容为空"}), 400

    # 获取向量嵌入
    embeddings = []
    for chunk in chunks:
        embedding = get_embedding(chunk["text"])
        if embedding is None:
            return jsonify({"error": f"获取向量嵌入失败: {chunk['text'][:50]}..."}), 500
        embeddings.append(embedding)

    # 插入数据库
    if not milvus_manager.insert_chunks(chunks, embeddings):
        return jsonify({"error": "插入向量数据库失败"}), 500

    # 删除临时文件
    try:
        os.remove(file_path)
    except:
        pass

    return jsonify({
        "message": "文档上传成功",
        "filename": file.filename,
        "chunks_count": len(chunks),
    })


@app.route("/api/query", methods=["POST"])
def query_knowledge():
    """
    基于知识库的问答

    参数:
        question: 问题文本
        top_k: 返回的相关文档数量（可选，默认 3）
    """
    data = request.get_json()
    question = data.get("question", "").strip()
    top_k = int(data.get("top_k", 3))

    if not question:
        return jsonify({"error": "问题不能为空"}), 400

    # 检查集合是否存在
    if not milvus_manager.connected:
        if not milvus_manager.connect():
            return jsonify({"error": "Milvus 连接失败"}), 500

    if not milvus_manager.ensure_collection():
        return jsonify({"error": "知识库为空，请先上传文档"}), 400

    # 获取问题的向量嵌入
    question_embedding = get_embedding(question)
    if question_embedding is None:
        return jsonify({"error": "获取问题向量嵌入失败"}), 500

    # 搜索相关文档
    search_results = milvus_manager.search(question_embedding, top_k)

    if not search_results:
        return jsonify({"error": "未找到相关文档"}), 404

    # 构建上下文
    context_parts = []
    for result in search_results:
        if milvus_manager.use_lite:
            text = result.get("text", "")
            score = result.get("distance", 0)
        else:
            text = result.entity.get("text", "")
            score = result.distance

        context_parts.append(f"[相关度: {1 - score:.4f}] {text}")

    context = "\n\n".join(context_parts)

    # 构建提示词
    system_prompt = """你是一个专业的问答助手。请基于以下参考信息回答用户的问题。

参考信息：
{context}

问题：{question}

要求：
1. 回答要基于参考信息，不要编造内容
2. 如果参考信息不足以回答问题，请明确说明
3. 回答要清晰、简洁、有条理
4. 使用中文回答

回答：""".format(context=context, question=question)

    messages = [{"role": "user", "content": system_prompt}]

    # 调用模型生成回答
    answer = chat_completion(messages)

    return jsonify({
        "question": question,
        "answer": answer,
        "sources": [
            {
                "text": r.get("text") if milvus_manager.use_lite else r.entity.get("text"),
                "source_file": r.get("source_file") if milvus_manager.use_lite else r.entity.get("source_file"),
                "score": 1 - r.get("distance", 0) if milvus_manager.use_lite else 1 - r.distance,
            }
            for r in search_results
        ],
    })


@app.route("/api/documents", methods=["GET"])
def get_documents():
    """获取向量数据库中的所有文档"""
    limit = int(request.args.get("limit", 100))

    if not milvus_manager.connected:
        if not milvus_manager.connect():
            return jsonify({"error": "Milvus 连接失败"}), 500

    documents = milvus_manager.get_all_data(limit)

    return jsonify({
        "count": len(documents),
        "documents": documents,
    })


@app.route("/api/clear", methods=["POST"])
def clear_knowledge_base():
    """清空知识库"""
    if milvus_manager.clear_collection():
        return jsonify({"message": "知识库已清空"})
    return jsonify({"error": "清空失败"}), 500


# ============================================================================
# 启动
# ============================================================================


def init_system():
    """初始化系统"""
    print("正在初始化知识库系统...")

    # 显示自动检测的模型
    print(f"\n检测到的模型:")
    if EMBEDDING_MODEL:
        print(f"  ✓ 嵌入模型: {EMBEDDING_MODEL}")
    else:
        print(f"  ✗ 嵌入模型: 未找到 (请运行: ollama pull nomic-embed-text:latest)")
    if CHAT_MODEL:
        print(f"  ✓ 问答模型: {CHAT_MODEL}")
    else:
        print(f"  ✗ 问答模型: 未找到 (请运行: ollama pull gemma3:1b)")

    if not EMBEDDING_MODEL or not CHAT_MODEL:
        print("\n警告: 缺少必要模型，部分功能可能无法使用")
        print("建议安装:")
        print("  ollama pull nomic-embed-text:latest")
        print("  ollama pull gemma3:1b")
        print()

    # 连接 Milvus
    print(f"连接 Milvus: {MILVUS_HOST}:{MILVUS_PORT}")
    if not milvus_manager.connect():
        print("警告: Milvus 连接失败，某些功能将不可用")

    # 测试 Ollama 连接
    print(f"测试 Ollama: {OLLAMA_BASE_URL}")
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            print("Ollama 连接成功")
            models = response.json().get("models", [])
            print(f"可用模型总数: {len(models)}")
        else:
            print("警告: Ollama 连接失败")
    except Exception as e:
        print(f"警告: 无法连接到 Ollama: {e}")

    # 确保 Milvus 集合存在
    if milvus_manager.connected:
        milvus_manager.ensure_collection()
        info = milvus_manager.get_collection_info()
        print(f"Milvus 集合状态: {info}")

    print("\n" + "=" * 40)
    print("系统初始化完成，访问 http://localhost:5001")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    init_system()
    print(f"\n启动 Web 服务器...")
    print(f"访问地址: http://localhost:5001")
    print(f"按 Ctrl+C 停止服务\n")
    app.run(host="0.0.0.0", port=5001, debug=False)
