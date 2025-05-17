from dataclasses import dataclass
from typing import Dict, List

import toml


@dataclass
class DatabaseConfig:
    user: str
    password: str
    name: str
    host: str
    port: int

    def __post_init__(self) -> None:
        self.uri = (
            f"postgresql+asyncpg://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.name}"
        )


@dataclass
class AppConfig:
    project_name: str
    api_v1_str: str


@dataclass
class LimitsConfig:
    daily_spending_limit: float
    weekly_spending_limit: float


@dataclass
class LoggingConfig:
    log_level: str


@dataclass
class CategorizationConfig:
    categories: List[str]
    default_category: str
    category_keywords: Dict[str, str]


@dataclass
class Config:
    db: DatabaseConfig
    app: AppConfig
    limits: LimitsConfig
    logging: LoggingConfig
    categorization: CategorizationConfig


def load_config(config_path: str) -> Config:
    with open(config_path, "r") as config_file:
        data = toml.load(config_file)

    return Config(
        db=DatabaseConfig(**data["db"]),
        app=AppConfig(**data["app"]),
        limits=LimitsConfig(**data["limits"]),
        logging=LoggingConfig(**data["logging"]),
        categorization=CategorizationConfig(
            categories=data["categorization"]["categories"],
            default_category=data["categorization"]["default_category"],
            category_keywords=data["categorization"]["category_keywords"],
        ),
    )
