#!/bin/bash
# 本地知识库问答系统启动脚本

cd "$(dirname "$0")"

echo "========================================="
echo "  本地知识库问答系统"
echo "========================================="

# 1. 检查 Ollama
echo -n "检查 Ollama..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo " ✅ 已运行"
else
    echo " ⏳ 启动中..."
    ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
fi

# 2. 清理旧的 Milvus 数据（可选，避免启动问题）
# rm -f milvus_data.db*

# 3. 启动应用
echo ""
echo "启动知识库系统..."
echo "访问地址: http://localhost:5001"
echo "按 Ctrl+C 停止"
echo ""
python3 app.py
