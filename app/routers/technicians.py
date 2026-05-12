from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import Technician, Withdrawal
from app.routers.deps import require_role


router = APIRouter(prefix="/tecnicos", tags=["tecnicos"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def list_technicians(request: Request, db: Session = Depends(get_db)) -> Response:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    technicians = db.scalars(select(Technician).order_by(Technician.active.desc(), Technician.name.asc())).all()
    return templates.TemplateResponse(request, "technicians.html", {"technicians": technicians, "error": None})


@router.post("")
def create_technician(
    request: Request,
    name: str = Form(...),
    role: str = Form("Tecnico"),
    db: Session = Depends(get_db),
) -> Response:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    technician = Technician(name=name.strip(), role=role.strip() or "Tecnico")
    db.add(technician)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        technicians = db.scalars(select(Technician).order_by(Technician.name.asc())).all()
        return templates.TemplateResponse(
            request,
            "technicians.html",
            {"technicians": technicians, "error": "Tecnico ja cadastrado."},
            status_code=400,
        )
    return RedirectResponse(url="/tecnicos", status_code=303)


@router.post("/{technician_id}/alternar")
def toggle_technician(technician_id: int, request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    technician = db.get(Technician, technician_id)
    if technician:
        technician.active = not technician.active
        db.commit()
    return RedirectResponse(url="/tecnicos", status_code=303)


@router.post("/{technician_id}/excluir")
def delete_technician(technician_id: int, request: Request, db: Session = Depends(get_db)) -> Response:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    technician = db.get(Technician, technician_id)
    if not technician:
        return RedirectResponse(url="/tecnicos", status_code=303)

    usage_count = db.scalar(select(func.count()).select_from(Withdrawal).where(Withdrawal.technician_id == technician_id)) or 0
    if usage_count:
        technicians = db.scalars(select(Technician).order_by(Technician.active.desc(), Technician.name.asc())).all()
        return templates.TemplateResponse(
            request,
            "technicians.html",
            {
                "technicians": technicians,
                "error": "Nao da para excluir tecnico com historico. Inative para manter os relatorios corretos.",
            },
            status_code=400,
        )

    db.delete(technician)
    db.commit()
    return RedirectResponse(url="/tecnicos", status_code=303)
