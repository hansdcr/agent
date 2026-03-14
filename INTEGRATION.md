# 前后端对接说明

## 概述

本文档说明如何启动和测试前后端对接功能。

## 后端（Python FastAPI）

### 1. 启动后端服务

```bash
cd /Users/gelin/Desktop/store/dev/python/ai/agent

# 确保已安装依赖
pip3 install fastapi uvicorn openai pydantic-settings

# 启动服务（默认端口8000）
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 后端API接口

- **聊天接口**: `POST http://localhost:8000/chat/`
  - 请求体:
    ```json
    {
      "message": "你好",
      "session_id": null  // 首次为null，后续使用返回的session_id
    }
    ```
  - 响应:
    ```json
    {
      "code": 200,
      "status": "success",
      "data": {
        "message": "AI的回复内容",
        "session_id": "uuid-string"
      },
      "message": "success"
    }
    ```

- **健康检查**: `GET http://localhost:8000/health`

### 3. CORS配置

后端已配置CORS，允许以下来源：
- `http://localhost:5173` (Vite默认端口)
- `http://localhost:3000`

## 前端（React + Vite）

### 1. 启动前端服务

```bash
cd /Users/gelin/Desktop/store/dev/python/ai/web-app

# 安装依赖（如果还没安装）
npm install

# 启动开发服务器（默认端口5173）
npm run dev
```

### 2. 访问聊天页面

打开浏览器访问：`http://localhost:5173/chat`

### 3. 功能说明

- 在聊天输入框中输入消息
- 点击"发送"按钮或按Enter键发送
- 消息会发送到后端API
- 后端调用DeepSeek模型生成回复
- 回复显示在聊天界面中
- 支持持续会话（通过session_id维护上下文）

## 测试步骤

1. **启动后端**
   ```bash
   cd /Users/gelin/Desktop/store/dev/python/ai/agent
   uvicorn main:app --reload
   ```

2. **启动前端**
   ```bash
   cd /Users/gelin/Desktop/store/dev/python/ai/web-app
   npm run dev
   ```

3. **测试对话**
   - 访问 http://localhost:5173/chat
   - 输入消息："你好"
   - 查看AI回复
   - 继续对话，测试会话连续性

## 技术栈

### 后端
- FastAPI
- OpenAI SDK (用于DeepSeek API)
- Pydantic Settings
- 日志系统

### 前端
- React 19
- Vite
- React Router
- i18next (国际化)

## 注意事项

1. 确保后端的 `.env` 文件中配置了正确的 `DEEPSEEK_API_KEY`
2. 后端必须先启动，前端才能正常工作
3. 如果修改了后端端口，需要同步修改前端的 `API_BASE_URL`（在 `src/components/ChatPage.jsx` 中）
4. 如果修改了前端端口，需要同步修改后端的CORS配置（在 `main.py` 中）

## 已完成的功能

- ✅ 后端CORS配置
- ✅ 前端ChatPage组件改造
- ✅ 消息发送和接收
- ✅ 会话管理（session_id）
- ✅ 加载状态显示
- ✅ 错误处理
- ✅ 消息历史显示
- ✅ 自动滚动到最新消息

## 下一步迭代建议

- 流式响应支持（使用 `/chat/stream` 接口）
- 消息持久化
- 用户认证
- 多会话管理
- 文件上传功能
- 语音输入
