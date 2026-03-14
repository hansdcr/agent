"""应用配置管理模块.

使用pydantic-settings管理应用配置，支持从环境变量和.env文件加载配置。
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类.

    管理DeepSeek API配置、模型参数和系统提示等配置项。
    配置优先级：环境变量 > .env文件 > 默认值

    Attributes:
        deepseek_api_key: DeepSeek API密钥
        deepseek_model: 使用的模型名称
        deepseek_base_url: API基础URL
        temperature: 生成温度参数(0.0-2.0)
        max_tokens: 最大生成token数
        system_prompt: 系统提示词
    """

    # DeepSeek API配置
    deepseek_api_key: str = Field(
        ...,
        description="DeepSeek API密钥",
        validation_alias="DEEPSEEK_API_KEY",
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        description="DeepSeek模型名称",
        validation_alias="DEEPSEEK_MODEL",
    )
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API基础URL",
        validation_alias="DEEPSEEK_BASE_URL",
    )

    # 模型参数
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="生成温度，控制随机性",
    )
    max_tokens: int = Field(
        default=2000,
        gt=0,
        description="最大生成token数",
    )

    # 系统配置
    system_prompt: str = Field(
        default="你是一个有帮助的AI助手。",
        description="系统提示词",
    )

    # 日志配置
    log_level: str = Field(
        default="INFO",
        description="日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）",
        validation_alias="LOG_LEVEL",
    )
    log_file: str = Field(
        default="logs/app.log",
        description="日志文件路径",
        validation_alias="LOG_FILE",
    )
    log_max_bytes: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="单个日志文件最大字节数",
        validation_alias="LOG_MAX_BYTES",
    )
    log_backup_count: int = Field(
        default=5,
        description="保留的日志文件备份数量",
        validation_alias="LOG_BACKUP_COUNT",
    )
    log_enable_color: bool = Field(
        default=True,
        description="是否启用彩色日志输出",
        validation_alias="LOG_ENABLE_COLOR",
    )

    # 数据库配置
    database_url: str = Field(
        default="postgresql://agent:agent123@localhost:5432/agent_db",
        description="PostgreSQL数据库连接URL",
        validation_alias="DATABASE_URL",
    )

    # 记忆系统配置
    memory_enabled: bool = Field(
        default=True,
        description="是否启用记忆系统",
        validation_alias="MEMORY_ENABLED",
    )
    memory_max_context_memories: int = Field(
        default=5,
        description="添加到上下文的最大记忆数量",
        validation_alias="MEMORY_MAX_CONTEXT_MEMORIES",
    )
    memory_cleanup_days: int = Field(
        default=30,
        description="记忆清理天数（短期记忆）",
        validation_alias="MEMORY_CLEANUP_DAYS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
