from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.security import token_bearer_valido
from app.mcp import tools

settings = get_settings()

mcp = FastMCP(
    "one-fianca-hermes",
    version=settings.app_version,
    instructions="Tools MCP em portugues para cadastros da One Fianca Locaticia.",
)
mcp.tool(tools.criar_imobiliaria)
mcp.tool(tools.obter_imobiliaria)
mcp.tool(tools.atualizar_imobiliaria)
mcp.tool(tools.remover_imobiliaria)
mcp.tool(tools.criar_corretor)
mcp.tool(tools.obter_corretor)
mcp.tool(tools.atualizar_corretor)
mcp.tool(tools.remover_corretor)
mcp.tool(tools.vincular_corretor_imobiliaria)
mcp.tool(tools.adicionar_observacao_parceiro)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        header = request.headers.get("authorization", "")
        esquema, _, token = header.partition(" ")
        if esquema.lower() != "bearer" or not token_bearer_valido(token):
            return JSONResponse({"detail": "token_mcp_invalido"}, status_code=401)
        return await call_next(request)


async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "one-mcp"})


app = mcp.http_app(path="/mcp", middleware=[Middleware(BearerAuthMiddleware)])
app.add_route("/health", health, methods=["GET"])
