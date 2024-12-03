# logger.py
import logging
import logging.handlers
from pathlib import Path

# Путь к директории для хранения логов
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Конфигурация логирования
LOG_FILE = LOG_DIR / 'bot.log'

# Создание логгера
logger = logging.getLogger('bot_logger')
logger.setLevel(logging.DEBUG)  # Уровень логирования

# Форматтер для логов
formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Уровень для консоли
console_handler.setFormatter(formatter)

# Файловый обработчик с ротацией
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)  # Уровень для файла
file_handler.setFormatter(formatter)

# Добавление обработчиков к логгеру
logger.addHandler(console_handler)
logger.addHandler(file_handler)
