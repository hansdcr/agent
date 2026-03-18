# Docker 部署指南

本指南说明如何使用 Docker 部署三个 AI Agent 服务，分别模拟李白、杜甫、白居易三位唐代诗人。

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- DeepSeek API Key

## 快速开始

### 1. 设置环境变量

在项目根目录创建 `.env` 文件（或者在启动前设置环境变量）：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，设置你的 DeepSeek API Key
DEEPSEEK_API_KEY=your_api_key_here
```

或者直接在命令行中设置：

```bash
export DEEPSEEK_API_KEY=your_api_key_here
```

### 2. 构建并启动服务

```bash
# 构建镜像并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问服务

服务启动后，可以通过以下端口访问：

- **李白 Agent**: http://localhost:9001
  - API 文档: http://localhost:9001/docs
  - 健康检查: http://localhost:9001/api/health

- **杜甫 Agent**: http://localhost:9002
  - API 文档: http://localhost:9002/docs
  - 健康检查: http://localhost:9002/api/health

- **白居易 Agent**: http://localhost:9003
  - API 文档: http://localhost:9003/docs
  - 健康检查: http://localhost:9003/api/health

- **PostgreSQL 数据库**: localhost:5432
  - 用户名: agent
  - 密码: agent123
  - 数据库: agent_db

## 服务说明

### 李白 (端口 9001)
- 性格：豪放不羁，浪漫主义诗人
- 特点：喜欢饮酒作诗，诗风飘逸洒脱
- Temperature: 0.8（更有创造性）

### 杜甫 (端口 9002)
- 性格：忧国忧民，现实主义诗人
- 特点：关注社会现实和民生疾苦，诗风沉郁
- Temperature: 0.7（平衡）

### 白居易 (端口 9003)
- 性格：通俗易懂，关注社会现实
- 特点：语言平实，诗风朴实
- Temperature: 0.7（平衡）

## 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 启动特定服务
docker-compose up -d libai
docker-compose up -d dufu
docker-compose up -d baijuyi

# 停止所有服务
docker-compose down

# 停止并删除数据卷（注意：会删除数据库数据）
docker-compose down -v

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f libai
docker-compose logs -f dufu
docker-compose logs -f baijuyi

# 进入容器
docker-compose exec libai sh
docker-compose exec postgres psql -U agent -d agent_db

# 重新构建镜像
docker-compose build --no-cache
```

## 测试服务

### 使用 curl 测试

```bash
# 测试李白服务
curl -X POST http://localhost:9001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下你自己",
    "user_id": "user123"
  }'

# 测试杜甫服务
curl -X POST http://localhost:9002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下你自己",
    "user_id": "user123"
  }'

# 测试白居易服务
curl -X POST http://localhost:9003/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下你自己",
    "user_id": "user123"
  }'
```

## 故障排查

### 服务无法启动

1. 检查 Docker 和 Docker Compose 版本
2. 确保端口 9001、9002、9003、5432 没有被占用
3. 检查 DEEPSEEK_API_KEY 是否正确设置

```bash
# 查看详细日志
docker-compose logs -f

# 检查端口占用
lsof -i :9001
lsof -i :9002
lsof -i :9003
lsof -i :5432
```

### 数据库连接失败

1. 确保 postgres 服务已启动并健康
2. 检查数据库连接字符串是否正确

```bash
# 检查 postgres 服务状态
docker-compose ps postgres

# 测试数据库连接
docker-compose exec postgres psql -U agent -d agent_db -c "SELECT 1;"
```

### API 调用失败

1. 检查 DEEPSEEK_API_KEY 是否有效
2. 检查网络连接
3. 查看服务日志

```bash
# 查看特定服务的日志
docker-compose logs -f libai
```

## 生产环境部署建议

1. **安全性**
   - 修改默认的数据库密码
   - 使用 secrets 管理敏感信息
   - 配置防火墙规则

2. **性能优化**
   - 根据负载调整容器资源限制
   - 配置数据库连接池
   - 使用反向代理（如 Nginx）

3. **监控和日志**
   - 配置日志收集（如 ELK Stack）
   - 设置监控告警（如 Prometheus + Grafana）
   - 定期备份数据库

4. **高可用性**
   - 使用 Docker Swarm 或 Kubernetes
   - 配置数据库主从复制
   - 实现负载均衡

## 开发模式

如果需要在开发模式下运行（支持热重载）：

```bash
# 修改 docker-compose.yml，添加卷挂载
# 在对应服务下添加：
volumes:
  - .:/app
  - /app/.venv  # 排除虚拟环境

# 然后重启服务
docker-compose up -d
```

## 清理

```bash
# 停止并删除所有容器
docker-compose down

# 删除镜像
docker rmi agent-libai agent-dufu agent-baijuyi

# 删除数据卷（注意：会删除所有数据）
docker volume rm agent_postgres_data

# 完全清理（包括未使用的镜像和卷）
docker system prune -a --volumes
```
