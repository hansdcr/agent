# 测试文档

本目录包含项目的所有测试文件。

## 测试文件说明

### test_api.py
测试原始架构的API接口。

**测试内容：**
- 原始FastAPI应用的基本功能
- 传统架构下的API端点

**运行方式：**
```bash
pytest tests/test_api.py -v
```

### test_ddd_api.py
测试DDD架构的API接口（主要测试文件）。

**测试内容：**
- 健康检查端点
- 聊天接口功能
- 会话连续性
- 输入验证

**运行方式：**
```bash
MEMORY_ENABLED=false pytest tests/test_ddd_api.py -v
```

**注意：** 使用 `MEMORY_ENABLED=false` 环境变量可以跳过数据库初始化，适合快速测试。

### test_ddd_domain.py
测试DDD领域模型。

**测试内容：**
- 领域实体（Conversation, Message等）
- 值对象（SessionId等）
- 领域逻辑

**运行方式：**
```bash
pytest tests/test_ddd_domain.py -v
```

## 运行所有测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行DDD相关测试（跳过数据库）
MEMORY_ENABLED=false pytest tests/test_ddd_api.py tests/test_ddd_domain.py -v
```

## 测试覆盖率

```bash
pytest tests/ --cov=src --cov-report=html
```

## 注意事项

1. DDD API测试需要FastAPI应用正常启动
2. 使用 `MEMORY_ENABLED=false` 可以跳过数据库依赖
3. 确保所有依赖已安装：`pip install -e .`
