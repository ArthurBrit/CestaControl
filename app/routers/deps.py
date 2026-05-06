from fastapi import Request
from fastapi.responses import RedirectResponse


def require_login(request: Request) -> None | RedirectResponse:
    if not request.session.get("user"):
        return RedirectResponse(url="/login", status_code=303)
    return None
