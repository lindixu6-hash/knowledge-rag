#!/bin/bash
# 本地知识库问答系统 - 启动脚本

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  本地知识库问答系统${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python 3${NC}"
    exit 1
fi

# 检查 Ollama
echo -e "${YELLOW}检查 Ollama 服务...${NC}"
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}错误: Ollama 服务未运行${NC}"
    echo "请先启动 Ollama: ollama serve"
    exit 1
fi
echo -e "${GREEN}✓ Ollama 服务正常${NC}"

# 检查模型
echo -e "${YELLOW}检查模型...${NC}"
MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4)

if echo "$MODELS" | grep -q "Qwen3-Embedding-0.6B"; then
    echo -e "${GREEN}✓ 向量模型 Qwen3-Embedding-0.6B 已安装${NC}"
else
    echo -e "${YELLOW}⚠ 向量模型未找到，请运行: ollama pull Qwen3-Embedding-0.6B:latest${NC}"
fi

if echo "$MODELS" | grep -q "gemma3:1b"; then
    echo -e "${GREEN}✓ 问答模型 gemma3:1b 已安装${NC}"
else
    echo -e "${YELLOW}⚠ 问答模型未找到，请运行: ollama pull gemma3:1b${NC}"
fi

# 检查依赖
echo -e "${YELLOW}检查 Python 依赖...${NC}"
if ! python3 -c "import flask, pymilvus" 2>/dev/null; then
    echo -e "${YELLOW}安装依赖...${NC}"
    pip install -r requirements.txt
fi
echo -e "${GREEN}✓ 依赖已安装${NC}"

# 进入项目目录
cd "$(dirname "$0")"

# 启动应用
echo ""
echo -e "${GREEN}启动应用...${NC}"
echo -e "访问地址: ${YELLOW}http://localhost:5000${NC}"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py
