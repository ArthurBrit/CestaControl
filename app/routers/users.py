from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import User
from app.routers.deps import ROLE_LABELS, require_role
from app.security import hash_password


router = APIRouter(prefix="/usuarios", tags=["usuarios"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def list_users(request: Request, db: Session = Depends(get_db)) -> Response:
    redirect = require_role(request, {"admin"})
    if redirect:
        return redirect

    users = db.scalars(select(User).order_by(User.active.desc(), User.full_name.asc())).all()
    return templates.TemplateResponse(request, "users.html", {"users": users, "roles": ROLE_LABELS, "error": None})


@router.post("")
def create_user(
    request: Request,
    username: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    role: str = Form("almoxarifado"),
    db: Session = Depends(get_db),
) -> Response:
    redirect = require_role(request, {"admin"})
    if redirect:
        return redirect

    if role not in ROLE_LABELS:
        role = "almoxarifado"

    user = User(
        username=username.strip(),
        full_name=full_name.strip(),
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        users = db.scalars(select(User).order_by(User.full_name.asc())).all()
        return templates.TemplateResponse(
            request,
            "users.html",
            {"users": users, "roles": ROLE_LABELS, "error": "Usuario ja cadastrado."},
            status_code=400,
        )
    return RedirectResponse(url="/usuarios", status_code=303)


@router.post("/{user_id}/senha")
def change_password(
    user_id: int,
    request: Request,
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    redirect = require_role(request, {"admin"})
    if redirect:
        return redirect

    user = db.get(User, user_id)
    if user and password:
        user.password_hash = hash_password(password)
        db.commit()
    return RedirectResponse(url="/usuarios", status_code=303)


@router.post("/{user_id}/perfil")
def change_role(
    user_id: int,
    request: Request,
    role: str = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    redirect = require_role(request, {"admin"})
    if redirect:
        return redirect

    user = db.get(User, user_id)
    if user and role in ROLE_LABELS:
        user.role = role
        db.commit()
    return RedirectResponse(url="/usuarios", status_code=303)


@router.post("/{user_id}/alternar")
def toggle_user(user_id: int, request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    redirect = require_role(request, {"admin"})
    if redirect:
        return redirect

    user = db.get(User, user_id)
    current_username = request.session.get("user")
    if user and user.username != current_username:
        user.active = not user.active
        db.commit()
    return RedirectResponse(url="/usuarios", status_code=303)
