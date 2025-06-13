"""
配置管理器
支持JSON配置文件和全局配置管理
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str
    host: str
    port: int
    username: str
    password: str
    database: str
    charset: str = "utf8mb4"
    pool_size: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    @property
    def url(self) -> str:
        """生成数据库连接URL"""
        if self.type == "mysql":
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"
        elif self.type == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == "sqlite":
            return f"sqlite:///{self.database}"
        else:
            raise ValueError(f"不支持的数据库类型: {self.type}")


@dataclass
class AppConfig:
    """应用配置"""
    name: str
    version: str
    debug: bool
    host: str
    port: int


@dataclass
class RedisConfig:
    """Redis配置"""
    host: str
    port: int
    db: int
    password: Optional[str] = None
    
    @property
    def url(self) -> str:
        """生成Redis连接URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        else:
            return f"redis://{self.host}:{self.port}/{self.db}"


@dataclass
class SecurityConfig:
    """安全配置"""
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


@dataclass
class CorsConfig:
    """CORS配置"""
    origins: List[str]


@dataclass
class SchedulerConfig:
    """调度器配置"""
    default_timeout: int
    max_retry_attempts: int
    default_thread_count: int
    check_interval: int


@dataclass
class ProxyConfig:
    """代理配置"""
    timeout: int
    rotation_enabled: bool
    fetch_interval: int


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str
    file: Optional[str]
    max_size: str
    retention: str


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self._config_data: Dict[str, Any] = {}
        self._app: Optional[AppConfig] = None
        self._database: Optional[DatabaseConfig] = None
        self._redis: Optional[RedisConfig] = None
        self._security: Optional[SecurityConfig] = None
        self._cors: Optional[CorsConfig] = None
        self._scheduler: Optional[SchedulerConfig] = None
        self._proxy: Optional[ProxyConfig] = None
        self._logging: Optional[LoggingConfig] = None
        
    def init(self) -> None:
        """初始化配置"""
        self._load_config()
        self._parse_config()
        
    def _load_config(self) -> None:
        """加载配置文件"""
        config_path = Path(self.config_file)
        
        # 如果不是绝对路径，则相对于当前工作目录查找
        if not config_path.is_absolute():
            # 尝试多个位置
            possible_paths = [
                Path.cwd() / self.config_file,
                Path.cwd() / "backend" / self.config_file,
                Path(__file__).parent.parent.parent / self.config_file,
            ]
            
            config_path = None
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break
            
            if config_path is None:
                raise FileNotFoundError(f"配置文件 {self.config_file} 未找到")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config_data = json.load(f)
        except Exception as e:
            raise ValueError(f"加载配置文件失败: {e}")
    
    def _parse_config(self) -> None:
        """解析配置数据"""
        try:
            # 解析应用配置
            app_data = self._config_data.get("app", {})
            self._app = AppConfig(**app_data)
            
            # 解析数据库配置
            db_data = self._config_data.get("database", {})
            self._database = DatabaseConfig(**db_data)
            
            # 解析Redis配置
            redis_data = self._config_data.get("redis", {})
            self._redis = RedisConfig(**redis_data)
            
            # 解析安全配置
            security_data = self._config_data.get("security", {})
            self._security = SecurityConfig(**security_data)
            
            # 解析CORS配置
            cors_data = self._config_data.get("cors", {})
            self._cors = CorsConfig(**cors_data)
            
            # 解析调度器配置
            scheduler_data = self._config_data.get("scheduler", {})
            self._scheduler = SchedulerConfig(**scheduler_data)
            
            # 解析代理配置
            proxy_data = self._config_data.get("proxy", {})
            self._proxy = ProxyConfig(**proxy_data)
            
            # 解析日志配置
            logging_data = self._config_data.get("logging", {})
            self._logging = LoggingConfig(**logging_data)
            
        except Exception as e:
            raise ValueError(f"解析配置数据失败: {e}")
    
    @property
    def app(self) -> AppConfig:
        """获取应用配置"""
        if self._app is None:
            raise RuntimeError("配置未初始化，请先调用 init() 方法")
        return self._app
    
    @property
    def database(self) -> DatabaseConfig:
        """获取数据库配置"""
        if self._database is None:
            raise RuntimeError("配置未初始化，请先调用 init() 方法")
        return self._database
    
    @property
    def redis(self) -> RedisConfig:
        """获取Redis配置"""
        if self._redis is None:
            raise RuntimeError("配置未初始化，请先调用 init() 方法")
        return self._redis
    
    @property
    def security(self) -> SecurityConfig:
        """获取安全配置"""
        if self._security is None:
            raise RuntimeError("配置未初始化，请先调用 init() 方法")
        return self._security
    
    @property
    def cors(self) -> CorsConfig:
        """获取CORS配置"""
        if self._cors is None:
            raise RuntimeError("配置未初始化，请先调用 init() 方法")
        return self._cors
    
    @property
    def scheduler(self) -> SchedulerConfig:
        """获取调度器配置"""
        if self._scheduler is None:
            raise RuntimeError("配置未初始化，请先调用 init() 方法")
        return self._scheduler
    
    @property
    def proxy(self) -> ProxyConfig:
        """获取代理配置"""
        if self._proxy is None:
            raise RuntimeError("配置未初始化，请先调用 init() 方法")
        return self._proxy
    
    @property
    def logging(self) -> LoggingConfig:
        """获取日志配置"""
        if self._logging is None:
            raise RuntimeError("配置未初始化，请先调用 init() 方法")
        return self._logging
    
    def get_raw_config(self) -> Dict[str, Any]:
        """获取原始配置数据"""
        return self._config_data.copy()
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """更新配置"""
        if section not in self._config_data:
            self._config_data[section] = {}
        self._config_data[section][key] = value
        self._parse_config()  # 重新解析配置
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"保存配置文件失败: {e}")


# 全局配置管理器实例
config_manager = ConfigManager()


def init_config(config_file: str = "config.json") -> None:
    """初始化全局配置"""
    global config_manager
    config_manager = ConfigManager(config_file)
    config_manager.init()


def get_config() -> ConfigManager:
    """获取全局配置管理器"""
    return config_manager 