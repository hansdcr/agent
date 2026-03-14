# 测试文档

本目录包含项目的所有测试文件。

## 测试文件说明

### test_ddd_api.py
测试DDD架构的API接口（主要测试文件）。

**测试内容：**
- 健康检查端点
- 聊天接口功能
- 会话连续性
- 输入验证

**运行方式：**
```bash
MEMORY_ENABLED=false uv run pytest tests/test_ddd_api.py -v
```

**注意：** 使用 `MEMORY_ENABLED=false` 环境变量可以跳过数据库初始化，适合快速测试。

### test_ddd_domain.py
测试DDD领域模型。

**测试内容：**
- 领域实体（Conversation, Message等）
- 值对象（SessionId, MessageRole, MessageContent等）
- 领域逻辑和验证规则

**运行方式：**
```bash
uv run pytest tests/test_ddd_domain.py -v
```

## 运行所有测试

```bash
# 运行所有测试
MEMORY_ENABLED=false uv run pytest tests/ -v

# 运行特定测试
uv run pytest tests/test_ddd_domain.py -v
```

## 测试覆盖率

```bash
uv run pytest tests/ --cov=src --cov-report=html
```

## 注意事项

1. 项目使用 uv 虚拟环境管理工具
2. DDD API测试需要FastAPI应用正常启动
3. 使用 `MEMORY_ENABLED=false` 可以跳过数据库依赖
4. 确保所有依赖已安装：`uv pip install -e .`
