# 使用 Python 3.12 作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# 复制项目文件
COPY pyproject.toml uv.lock ./
COPY main.py ./
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# 安装 Python 依赖
RUN uv sync --frozen

# 暴露端口（将在 docker-compose 中指定具体端口）
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
