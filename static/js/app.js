/**
 * 本地知识库问答系统 - 前端逻辑
 *
 * 功能：
 * - 系统状态监控
 * - 文档上传处理
 * - 智能问答交互
 * - 知识库文档查看
 */

// ============================================================================
// API 基础配置
// ============================================================================

const API_BASE = "";  // 相对路径，与后端同域

// ============================================================================
// 工具函数
// ============================================================================

/**
 * 显示加载状态
 */
function showLoading(element) {
    element.innerHTML = '<div class="loading">加载中...</div>';
}

/**
 * 显示错误消息
 */
function showError(element, message) {
    element.innerHTML = `<div class="upload-result error">${message}</div>`;
    element.style.display = "block";
}

/**
 * 显示成功消息
 */
function showSuccess(element, message) {
    element.innerHTML = `<div class="upload-result success">${message}</div>`;
    element.style.display = "block";
}

/**
 * 转义 HTML 特殊字符
 */
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// 系统状态
// ============================================================================

/**
 * 获取并显示系统状态
 */
async function refreshStatus() {
    const statusContent = document.getElementById("statusContent");
    showLoading(statusContent);

    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();

        const ollama = data.ollama || {};
        const milvus = data.milvus || {};

        statusContent.innerHTML = `
            <div class="status-card ollama">
                <div class="status-card-title">Ollama 服务</div>
                <div class="status-indicator">
                    <span class="status-dot ${ollama.connected ? 'connected' : 'disconnected'}"></span>
                    <span>${ollama.connected ? '已连接' : '未连接'}</span>
                </div>
                ${ollama.models && ollama.models.length > 0 ? `
                    <div class="model-list">
                        ${ollama.models.map(m => `<span class="model-tag">${escapeHtml(m)}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
            <div class="status-card milvus">
                <div class="status-card-title">Milvus 向量库</div>
                <div class="status-indicator">
                    <span class="status-dot ${milvus.connected ? 'connected' : 'disconnected'}"></span>
                    <span>${milvus.connected ? '已连接' : '未连接'}</span>
                </div>
                ${milvus.count !== undefined ? `
                    <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-secondary);">
                        文档数量: ${milvus.count}
                    </div>
                ` : ''}
            </div>
            <div class="status-card">
                <div class="status-card-title">配置信息</div>
                <div class="status-card-value" style="font-size: 0.85rem; color: var(--text-secondary);">
                    向量模型: ${escapeHtml(data.embedding_model || 'N/A')}<br>
                    问答模型: ${escapeHtml(data.chat_model || 'N/A')}
                </div>
            </div>
        `;
    } catch (error) {
        statusContent.innerHTML = `
            <div class="status-card" style="border-color: var(--danger-color);">
                <div class="status-card-value">获取状态失败: ${escapeHtml(error.message)}</div>
            </div>
        `;
    }
}

// ============================================================================
// 文档上传
// ============================================================================

/**
 * 处理文档上传
 */
async function handleUpload(event) {
    event.preventDefault();

    const form = event.target;
    const fileInput = document.getElementById("fileInput");
    const chunkSizeInput = document.getElementById("chunkSize");
    const separatorInput = document.getElementById("separator");
    const resultDiv = document.getElementById("uploadResult");

    const file = fileInput.files[0];
    if (!file) {
        showError(resultDiv, "请选择文件");
        return;
    }

    // 转换分隔符
    const separator = separatorInput.value
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\t", "\t");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("chunk_size", chunkSizeInput.value);
    formData.append("separator", separator);

    showLoading(resultDiv);
    resultDiv.style.display = "block";

    try {
        const response = await fetch(`${API_BASE}/api/upload`, {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess(resultDiv, `
                <strong>上传成功！</strong><br>
                文件: ${escapeHtml(data.filename)}<br>
                分块数量: ${data.chunks_count}
            `);
            form.reset();
            refreshStatus();  // 刷新状态以显示新的文档数量
        } else {
            showError(resultDiv, `上传失败: ${escapeHtml(data.error || '未知错误')}`);
        }
    } catch (error) {
        showError(resultDiv, `上传失败: ${escapeHtml(error.message)}`);
    }
}

// ============================================================================
// 智能问答
// ============================================================================

/**
 * 处理问答请求
 */
async function handleQuery(event) {
    event.preventDefault();

    const questionInput = document.getElementById("questionInput");
    const topKSelect = document.getElementById("topK");
    const resultDiv = document.getElementById("queryResult");

    const question = questionInput.value.trim();
    if (!question) {
        resultDiv.innerHTML = `
            <div class="upload-result error" style="display:block;">请输入问题</div>
        `;
        return;
    }

    showLoading(resultDiv);

    try {
        const response = await fetch(`${API_BASE}/api/query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                question: question,
                top_k: parseInt(topKSelect.value),
            }),
        });

        const data = await response.json();

        if (response.ok) {
            displayAnswer(data);
        } else {
            resultDiv.innerHTML = `
                <div class="upload-result error" style="display:block;">
                    ${escapeHtml(data.error || '未知错误')}
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="upload-result error" style="display:block;">
                请求失败: ${escapeHtml(error.message)}
            </div>
        `;
    }
}

/**
 * 显示问答结果
 */
function displayAnswer(data) {
    const resultDiv = document.getElementById("queryResult");

    const sourcesHtml = data.sources && data.sources.length > 0 ? `
        <div class="sources-section">
            <div class="sources-title">参考来源</div>
            ${data.sources.map(source => `
                <div class="source-item">
                    <div class="source-header">
                        <span class="source-file">${escapeHtml(source.source_file || '未知来源')}</span>
                        <span class="source-score">相关度: ${(source.score * 100).toFixed(1)}%</span>
                    </div>
                    <div class="source-text">${escapeHtml(source.text || '')}</div>
                </div>
            `).join('')}
        </div>
    ` : '';

    resultDiv.innerHTML = `
        <div class="qa-answer">
            <div class="answer-card">
                <div class="answer-header">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                    <span>回答</span>
                </div>
                <div class="answer-content">${escapeHtml(data.answer || '暂无回答')}</div>
                ${sourcesHtml}
            </div>
        </div>
    `;
}

// ============================================================================
// 文档列表
// ============================================================================

/**
 * 打开文档列表模态框
 */
async function openDocsModal() {
    const modal = document.getElementById("docsModal");
    const docsList = document.getElementById("docsList");

    modal.classList.add("active");
    showLoading(docsList);

    try {
        const response = await fetch(`${API_BASE}/api/documents?limit=200`);
        const data = await response.json();

        if (response.ok && data.documents && data.documents.length > 0) {
            docsList.innerHTML = data.documents.map((doc, index) => `
                <div class="doc-item">
                    <div class="doc-header">
                        <span class="doc-file">${escapeHtml(doc.source_file || '未知文件')}</span>
                        <span class="doc-index">#${doc.chunk_index + 1}</span>
                    </div>
                    <div class="doc-text">${escapeHtml(doc.text || '')}</div>
                </div>
            `).join('');
        } else {
            docsList.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    暂无文档
                </div>
            `;
        }
    } catch (error) {
        docsList.innerHTML = `
            <div class="upload-result error" style="display:block;">
                加载失败: ${escapeHtml(error.message)}
            </div>
        `;
    }
}

/**
 * 关闭文档列表模态框
 */
function closeDocsModal() {
    const modal = document.getElementById("docsModal");
    modal.classList.remove("active");
}

// ============================================================================
// 清空知识库
// ============================================================================

/**
 * 清空知识库
 */
async function clearKnowledgeBase() {
    if (!confirm("确定要清空所有文档吗？此操作不可恢复！")) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/clear`, {
            method: "POST",
        });

        const data = await response.json();

        if (response.ok) {
            alert("知识库已清空");
            refreshStatus();
        } else {
            alert(`清空失败: ${data.error || '未知错误'}`);
        }
    } catch (error) {
        alert(`清空失败: ${error.message}`);
    }
}

// ============================================================================
// 事件监听
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
    // 刷新状态按钮
    document.getElementById("refreshStatusBtn").addEventListener("click", refreshStatus);

    // 上传表单
    document.getElementById("uploadForm").addEventListener("submit", handleUpload);

    // 问答表单
    document.getElementById("queryForm").addEventListener("submit", handleQuery);

    // 查看文档按钮
    document.getElementById("viewDocsBtn").addEventListener("click", openDocsModal);

    // 清空按钮
    document.getElementById("clearBtn").addEventListener("click", clearKnowledgeBase);

    // 模态框关闭
    document.querySelector(".modal-close").addEventListener("click", closeDocsModal);
    document.getElementById("docsModal").addEventListener("click", (e) => {
        if (e.target.id === "docsModal") {
            closeDocsModal();
        }
    });

    // 初始加载状态
    refreshStatus();
});
