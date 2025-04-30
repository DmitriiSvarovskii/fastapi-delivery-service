from pydantic_settings import BaseSettings


class TaskSettings(BaseSettings):
    calculator_retry_countdown: int = 10
    calculator_max_retries: int = 3
    db_retry_countdown: int = 30
    db_max_retries: int = 5


task_settings = TaskSettings()


class CalculatorSettings(BaseSettings):
    redis_key: str = "cbr_usd_rate"
    cache_ttl: int = 60 * 5
    http_timeout: int = 5
    weight_factor: float = 0.5
    value_factor: float = 0.01


calculator_settings = CalculatorSettings()
