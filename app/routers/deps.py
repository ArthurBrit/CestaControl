from fastapi import Request
from fastapi.responses import RedirectResponse


ROLE_LABELS = {
    "admin": "Administrador",
    "almoxarifado": "Almoxarifado",
    "consulta": "Consulta",
}


def require_login(request: Request) -> None | RedirectResponse:
    if not request.session.get("user"):
        return RedirectResponse(url="/login", status_code=303)
    return None


def require_role(request: Request, allowed_roles: set[str]) -> None | RedirectResponse:
    redirect = require_login(request)
    if redirect:
        return redirect

    role = request.session.get("user_role")
    if role not in allowed_roles:
        return RedirectResponse(url="/", status_code=303)
    return None


def can_manage_stock(request: Request) -> bool:
    return request.session.get("user_role") in {"admin", "almoxarifado"}


def can_manage_users(request: Request) -> bool:
    return request.session.get("user_role") == "admin"
