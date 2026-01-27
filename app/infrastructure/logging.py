import logging
import json
import os
from typing import Any, Dict


class JsonLogger:
    def __init__(self, service: str, env: str = None):
        self.service = service
        self.env = env or os.getenv("ENV", "dev")
        self.level = os.getenv("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(service)
        self.logger.setLevel(self.level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.handlers = [handler]

    def log(self, level: str, message: str, extra: Dict[str, Any]):
        log_entry = {
            "timestamp": extra.get("timestamp"),
            "level": level,
            "service": self.service,
            "env": self.env,
            "request_id": extra.get("request_id"),
            "message": message,
        }
        # Add HTTP fields if present
        for field in [
            "http.method",
            "http.path",
            "http.status_code",
            "duration_ms",
            "error.code",
            "user_id",
            "client_ip",
        ]:
            if field in extra:
                log_entry[field] = extra[field]
        self.logger.log(
            getattr(logging, level), json.dumps(log_entry, ensure_ascii=False)
        )

    def info(self, message: str, extra: Dict[str, Any]):
        self.log("INFO", message, extra)

    def error(self, message: str, extra: Dict[str, Any]):
        self.log("ERROR", message, extra)

    def warning(self, message: str, extra: Dict[str, Any]):
        self.log("WARNING", message, extra)

    def debug(self, message: str, extra: Dict[str, Any]):
        self.log("DEBUG", message, extra)

    def critical(self, message: str, extra: Dict[str, Any]):
        self.log("CRITICAL", message, extra)


# LGPD: Anonimização/máscara de IP


def mask_ip(ip: str) -> str:
    if not ip:
        return None
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.x.x"
    return "x.x.x.x"


# LGPD: Anonimização de user_id (exemplo: hash/truncamento)
def mask_user_id(user_id: str) -> str:
    if not user_id:
        return None
    return user_id[:6] + "..."
