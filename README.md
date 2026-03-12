# AI Agent - 智能对话系统

基于DeepSeek的AI智能体，支持多轮对话、流式响应和会话管理。

## 项目简介

这是一个高度拟人化的AI智能体项目，采用渐进式开发方式，从基础对话功能开始，逐步迭代实现记忆系统、情感系统等高级特性。

### 当前版本：v0.1.0（迭代一）

**已实现功能**：
- ✅ 基于FastAPI的异步Web服务
- ✅ DeepSeek API集成
- ✅ 多轮对话支持
- ✅ 流式响应（Server-Sent Events）
- ✅ 会话管理
- ✅ 配置管理
- ✅ 完整的单元测试

## 技术栈

- **Web框架**：FastAPI + Uvicorn
- **AI模型**：DeepSeek API
- **异步编程**：asyncio + aiohttp
- **配置管理**：Pydantic Settings
- **测试框架**：pytest + pytest-asyncio
- **代码质量**：black + ruff

## 快速开始

### 1. 环境要求

- Python 3.12+
- uv（Python包管理工具）

### 2. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd agent

# 安装依赖
uv pip install -e .
```

### 3. 配置API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的DeepSeek API Key
# DEEPSEEK_API_KEY=your_api_key_here
```

获取API Key：访问 [DeepSeek官网](https://platform.deepseek.com/) 注册并获取。

### 4. 启动服务

```bash
# 开发模式（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

服务启动后，访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## API接口

### 1. 健康检查

```bash
GET /health
```

**响应示例**：
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### 2. 普通对话

```bash
POST /chat/
Content-Type: application/json

{
  "message": "你好",
  "session_id": null
}
```

**响应示例**：
```json
{
  "message": "你好！我是DeepSeek AI助手，很高兴为你服务。",
  "session_id": "uuid-xxx-xxx"
}
```

**多轮对话**：
```bash
# 使用返回的session_id继续对话
POST /chat/
{
  "message": "介绍一下你自己",
  "session_id": "uuid-xxx-xxx"
}
```

### 3. 流式对话

```bash
POST /chat/stream
Content-Type: application/json

{
  "message": "用一句话介绍Python",
  "session_id": null
}
```

**响应格式**（Server-Sent Events）：
```
data: {'session_id': 'uuid-xxx-xxx'}

data: {'content': 'Python'}

data: {'content': '是一种'}

data: {'content': '简洁易读的'}

...

data: {'done': true}
```

## 使用示例

### cURL示例

```bash
# 普通对话
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'

# 流式对话
curl -N -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "介绍一下人工智能"}'
```

### Python示例

```python
import asyncio
import aiohttp

async def chat():
    async with aiohttp.ClientSession() as session:
        # 普通对话
        async with session.post(
            "http://localhost:8000/chat/",
            json={"message": "你好"}
        ) as resp:
            data = await resp.json()
            print(f"AI: {data['message']}")
            session_id = data['session_id']

        # 继续对话
        async with session.post(
            "http://localhost:8000/chat/",
            json={"message": "再见", "session_id": session_id}
        ) as resp:
            data = await resp.json()
            print(f"AI: {data['message']}")

asyncio.run(chat())
```

## 项目结构

```
agent/
├── docs/                    # 文档
│   ├── requirements.md      # 总体需求文档
│   ├── iteration_01.md      # 迭代一计划
│   └── coding_standards.md  # 编码规范
├── src/                     # 源代码
│   ├── api/                 # API接口
│   │   ├── models/          # 请求/响应模型
│   │   └── routes/          # 路由
│   ├── config/              # 配置管理
│   └── core/                # 核心业务逻辑
│       ├── llm.py          # LLM客户端
│       └── conversation.py  # 对话管理
├── tests/                   # 测试
│   └── test_api.py         # API测试
├── main.py                  # 应用入口
├── pyproject.toml           # 项目配置
├── .env.example             # 环境变量模板
└── README.md                # 本文件
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_api.py::test_chat_endpoint -v

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

### 代码检查

```bash
# 代码格式化
black src/ tests/

# 代码检查
ruff check src/ tests/

# 类型检查（可选）
mypy src/
```

### 编码规范

本项目遵循以下规范：
- Google Python编码规范
- 每个方法不超过50行（最多100行）
- 完整的类型注解和docstring
- 使用black进行代码格式化
- 使用ruff进行代码检查

详见：[docs/coding_standards.md](docs/coding_standards.md)

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DEEPSEEK_API_KEY | DeepSeek API密钥 | 必填 |
| DEEPSEEK_MODEL | 模型名称 | deepseek-chat |
| DEEPSEEK_BASE_URL | API基础URL | https://api.deepseek.com |
| TEMPERATURE | 生成温度（0.0-2.0） | 0.7 |
| MAX_TOKENS | 最大生成token数 | 2000 |
| SYSTEM_PROMPT | 系统提示词 | 你是一个有帮助的AI助手。 |

### 模型选择

- `deepseek-chat`：DeepSeek-V3.2 非思考模式（推荐）
- `deepseek-reasoner`：DeepSeek-V3.2 思考模式

## 后续规划

### 迭代二：记忆系统基础（计划中）
- 短期记忆（会话级别）
- 长期记忆（向量数据库）
- 记忆检索与整合

### 迭代三：情感系统雏形（计划中）
- 基础情感识别
- 情感状态存储
- 情感驱动的回复

### 迭代四：多模型支持（计划中）
- 抽象LLM接口
- 支持Claude、GPT等
- 模型切换功能

详见：[docs/requirements.md](docs/requirements.md)

## 常见问题

### Q: 如何切换到思考模式？

A: 在.env文件中设置：
```bash
DEEPSEEK_MODEL=deepseek-reasoner
```

### Q: 如何调整回复的创造性？

A: 修改TEMPERATURE参数（0.0-2.0）：
- 0.0-0.3：更确定、更保守
- 0.7：平衡（默认）
- 1.0-2.0：更有创造性、更随机

### Q: 会话会保存多久？

A: 当前版本会话存储在内存中，服务重启后会丢失。迭代二将实现持久化存储。

### Q: 如何限制回复长度？

A: 修改MAX_TOKENS参数，例如：
```bash
MAX_TOKENS=500  # 限制为500个token
```

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 开启Pull Request

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 联系方式

- 项目地址：[GitHub Repository]
- 问题反馈：[GitHub Issues]
- 文档：[docs/](docs/)

## 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供强大的AI模型
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Web框架
- [Anthropic Claude](https://www.anthropic.com/) - 开发辅助

---

**版本**：v0.1.0
**更新日期**：2026-03-12
**开发状态**：活跃开发中
