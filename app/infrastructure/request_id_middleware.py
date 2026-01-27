import uuid
from fastapi import Request

REQUEST_ID_HEADER = "X-Request-Id"


class RequestIdMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            request_id = headers.get(REQUEST_ID_HEADER.lower().encode(), None)
            if request_id:
                request_id = request_id.decode()
            else:
                request_id = f"req_{uuid.uuid4().hex[:16]}"
            scope["request_id"] = request_id

            async def send_with_request_id(message):
                if message["type"] == "http.response.start":
                    headers = message.setdefault("headers", [])
                    headers.append((REQUEST_ID_HEADER.encode(), request_id.encode()))
                await send(message)

            await self.app(scope, receive, send_with_request_id)
        else:
            await self.app(scope, receive, send)


# Utilitário para obter o request_id em rotas


def get_request_id(request: Request) -> str:
    return getattr(request, "scope", {}).get("request_id", None)
