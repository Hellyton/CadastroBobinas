from loguru import logger

logger.add(
    "logs/cadastro.log",
    rotation="1 MB",
    encoding="utf-8"
)