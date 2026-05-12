from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import InventoryItem, InventoryMovement, Technician, Withdrawal
from app.routers.deps import require_role


router = APIRouter(prefix="/retiradas", tags=["retiradas"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/nova", response_class=HTMLResponse)
def new_withdrawal(request: Request, db: Session = Depends(get_db)) -> Response:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    technicians = db.scalars(select(Technician).where(Technician.active.is_(True)).order_by(Technician.name.asc())).all()
    items = db.scalars(select(InventoryItem).where(InventoryItem.active.is_(True)).order_by(InventoryItem.name.asc())).all()
    return templates.TemplateResponse(
        request,
        "withdrawal_form.html",
        {"technicians": technicians, "items": items, "today": date.today(), "error": None},
    )


@router.post("")
def create_withdrawal(
    request: Request,
    technician_id: int = Form(...),
    item_id: int = Form(...),
    quantity: int = Form(...),
    withdrawn_at: date = Form(...),
    companion_name: str = Form(...),
    destination: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
) -> Response:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    item = db.get(InventoryItem, item_id)
    technician = db.get(Technician, technician_id)
    if not item or not technician or quantity <= 0 or item.stock < quantity or not companion_name.strip():
        technicians = db.scalars(select(Technician).where(Technician.active.is_(True)).order_by(Technician.name.asc())).all()
        items = db.scalars(select(InventoryItem).where(InventoryItem.active.is_(True)).order_by(InventoryItem.name.asc())).all()
        error = "Confira tecnico, acompanhante, item e quantidade. O estoque precisa ser suficiente."
        return templates.TemplateResponse(
            request,
            "withdrawal_form.html",
            {"technicians": technicians, "items": items, "today": withdrawn_at, "error": error},
            status_code=400,
        )

    item.stock -= quantity
    db.add(
        Withdrawal(
            technician_id=technician_id,
            item_id=item_id,
            quantity=quantity,
            withdrawn_at=withdrawn_at,
            companion_name=companion_name.strip(),
            destination=destination.strip() or None,
            notes=notes.strip() or None,
        )
    )
    db.add(
        InventoryMovement(
            item_id=item_id,
            movement_type="saida",
            quantity=-quantity,
            balance_after=item.stock,
            reason=f"Retirada para visita - {technician.name}",
            created_by=request.session.get("user"),
        )
    )
    db.commit()
    return RedirectResponse(url="/historico", status_code=303)


@router.get("/historico", response_class=HTMLResponse)
@router.get("/historico/", response_class=HTMLResponse)
def legacy_history_redirect() -> RedirectResponse:
    return RedirectResponse(url="/historico", status_code=303)


@router.get("/excluir/{withdrawal_id}")
def delete_withdrawal_legacy(withdrawal_id: int) -> RedirectResponse:
    return RedirectResponse(url=f"/historico/{withdrawal_id}/excluir", status_code=303)
