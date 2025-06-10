import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    @staticmethod
    def setup(
        name: str = "PatifeUpdater",
        log_dir: str = "./logs",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 3
    ) -> logging.Logger:
        """
        Configura e retorna um logger com:
        - Console handler (INFO+)
        - RotatingFileHandler (DEBUG+)
        O arquivo de log fica em <log_dir>/<name>.log.
        """
        log_directory = Path(log_dir)
        log_directory.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Evita adicionar múltiplos handlers
        if not logger.handlers:
            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_fmt = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_fmt)
            logger.addHandler(console_handler)

            # Handler para ficheiro com rotação
            file_handler = RotatingFileHandler(
                log_directory / f"{name}.log",
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            file_handler.setLevel(file_level)
            file_fmt = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_fmt)
            logger.addHandler(file_handler)

        return logger
