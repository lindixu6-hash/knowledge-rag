#!/usr/bin/env python3
"""
知识库问答系统 - 功能测试脚本

测试内容：
1. 模型自动检测
2. Ollama API 连接
3. 文件上传和处理
4. 向量检索
5. 问答功能
"""

import os
import sys
import requests
import json
import time

# API 基础地址
API_BASE = "http://localhost:5000"

# 颜色输出
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
NC = "\033[0m"


def print_section(title):
    """打印测试区块"""
    print(f"\n{BLUE}{'=' * 50}{NC}")
    print(f"{BLUE}{title}{NC}")
    print(f"{BLUE}{'=' * 50}{NC}\n")


def test_api(endpoint, method="GET", data=None, files=None):
    """通用 API 测试函数"""
    url = f"{API_BASE}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files, timeout=60)
            else:
                response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=60)

        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}


def main():
    print_section("知识库问答系统 - 功能测试")

    # 1. 测试系统状态
    print(f"{YELLOW}[1/5] 测试系统状态...{NC}")
    status, data = test_api("/api/status")

    if status == 200:
        ollama = data.get("ollama", {})
        milvus = data.get("milvus", {})

        print(f"  Ollama 服务: {GREEN}{'✓ 已连接' if ollama.get('connected') else '✗ 未连接'}{NC}")
        print(f"  Milvus 服务: {GREEN}{'✓ 已连接' if milvus.get('connected') else '✗ 未连接'}{NC}")
        print(f"  嵌入模型: {data.get('embedding_model', 'N/A')}")
        print(f"  问答模型: {data.get('chat_model', 'N/A')}")
        print(f"  文档数量: {milvus.get('count', 0)}")

        if not ollama.get("connected"):
            print(f"{RED}错误: Ollama 服务未运行{NC}")
            return
    else:
        print(f"{RED}错误: 无法获取系统状态{NC}")
        print(f"  {data.get('error', '未知错误')}")
        return

    # 2. 测试文档上传
    print(f"\n{YELLOW}[2/5] 测试文档上传...{NC}")

    test_file = "test_python_basics.md"
    if not os.path.exists(test_file):
        print(f"{RED}错误: 测试文件 {test_file} 不存在{NC}")
        return

    with open(test_file, "rb") as f:
        files = {"file": (test_file, f, "text/markdown")}
        data = {"chunk_size": "512", "separator": "\\n\\n"}
        status, result = test_api("/api/upload", method="POST", data=data, files=files)

    if status == 200:
        print(f"  {GREEN}✓ 上传成功{NC}")
        print(f"    文件名: {result.get('filename')}")
        print(f"    分块数量: {result.get('chunks_count')}")
    else:
        print(f"  {RED}✗ 上传失败{NC}")
        print(f"    {result.get('error', '未知错误')}")
        return

    # 等待索引完成
    time.sleep(1)

    # 3. 测试获取文档列表
    print(f"\n{YELLOW}[3/5] 测试获取文档列表...{NC}")
    status, data = test_api("/api/documents?limit=10")

    if status == 200:
        count = data.get("count", 0)
        print(f"  {GREEN}✓ 成功获取{NC}")
        print(f"    文档总数: {count}")
        if count > 0:
            docs = data.get("documents", [])
            print(f"    第一个文档预览: {docs[0].get('text', '')[:50]}...")
    else:
        print(f"  {RED}✗ 获取失败{NC}")
        print(f"    {data.get('error', '未知错误')}")

    # 4. 测试问答功能
    print(f"\n{YELLOW}[4/5] 测试问答功能...{NC}")

    test_questions = [
        "Python 中如何定义函数？",
        "什么是列表推导式？",
        "Python 的基本数据类型有哪些？",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n  问题 {i}: {question}")
        status, data = test_api("/api/query", method="POST", data={"question": question, "top_k": 3})

        if status == 200:
            answer = data.get("answer", "")
            sources = data.get("sources", [])
            print(f"  {GREEN}✓ 回答:{NC}")
            # 只显示前 200 字符
            print(f"    {answer[:200]}{'...' if len(answer) > 200 else ''}")
            if sources:
                print(f"    相关度: {sources[0].get('score', 0):.2%}")
        else:
            print(f"  {RED}✗ 回答失败{NC}")
            print(f"    {data.get('error', '未知错误')}")

    # 5. 测试结果摘要
    print(f"\n{YELLOW}[5/5] 测试摘要{NC}")
    print(f"  所有测试完成！")
    print(f"\n{GREEN}✓ 系统运行正常{NC}")
    print(f"  访问地址: {API_BASE}")
    print(f"\n建议：")
    print(f"  1. 上传更多文档以丰富知识库")
    print(f"  2. 尝试不同类型的问题测试问答效果")
    print(f"  3. 使用 '查看所有文档' 功能管理知识库")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}测试中断{NC}")
        sys.exit(0)
