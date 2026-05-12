from datetime import date

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import InventoryItem, InventoryMovement, Technician, Withdrawal
from app.routers.deps import require_login, require_role
from app.services.exports import build_excel_report, build_pdf_report


router = APIRouter(tags=["relatorios"])
templates = Jinja2Templates(directory="app/templates")


def _filtered_withdrawals(
    start_date: date | None,
    end_date: date | None,
    technician_id: int | None,
    item_id: int | None,
) -> Select[tuple[Withdrawal]]:
    stmt = select(Withdrawal).join(Withdrawal.technician).join(Withdrawal.item)
    if start_date:
        stmt = stmt.where(Withdrawal.withdrawn_at >= start_date)
    if end_date:
        stmt = stmt.where(Withdrawal.withdrawn_at <= end_date)
    if technician_id:
        stmt = stmt.where(Withdrawal.technician_id == technician_id)
    if item_id:
        stmt = stmt.where(Withdrawal.item_id == item_id)
    return stmt.order_by(Withdrawal.withdrawn_at.desc(), Withdrawal.id.desc())


def _summary_query(
    start_date: date | None,
    end_date: date | None,
    technician_id: int | None,
    item_id: int | None,
):
    stmt = (
        select(
            Technician.name.label("technician_name"),
            InventoryItem.name.label("item_name"),
            func.sum(Withdrawal.quantity).label("total"),
        )
        .join(Withdrawal.technician)
        .join(Withdrawal.item)
        .group_by(Technician.name, InventoryItem.name)
        .order_by(Technician.name.asc(), InventoryItem.name.asc())
    )
    if start_date:
        stmt = stmt.where(Withdrawal.withdrawn_at >= start_date)
    if end_date:
        stmt = stmt.where(Withdrawal.withdrawn_at <= end_date)
    if technician_id:
        stmt = stmt.where(Withdrawal.technician_id == technician_id)
    if item_id:
        stmt = stmt.where(Withdrawal.item_id == item_id)
    return stmt


@router.get("/historico", response_class=HTMLResponse)
def history(
    request: Request,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    technician_id: int | None = Query(None),
    item_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> Response:
    redirect = require_login(request)
    if redirect:
        return redirect

    withdrawals = db.scalars(_filtered_withdrawals(start_date, end_date, technician_id, item_id)).all()
    summary = db.execute(_summary_query(start_date, end_date, technician_id, item_id)).all()
    technicians = db.scalars(select(Technician).order_by(Technician.name.asc())).all()
    items = db.scalars(select(InventoryItem).order_by(InventoryItem.name.asc())).all()
    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "withdrawals": withdrawals,
            "summary": summary,
            "technicians": technicians,
            "items": items,
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "technician_id": technician_id,
                "item_id": item_id,
            },
        },
    )


@router.post("/historico/{withdrawal_id}/excluir")
def delete_withdrawal(withdrawal_id: int, request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    withdrawal = db.get(Withdrawal, withdrawal_id)
    if withdrawal:
        item = db.get(InventoryItem, withdrawal.item_id)
        if item:
            item.stock += withdrawal.quantity
            db.add(
                InventoryMovement(
                    item_id=item.id,
                    movement_type="devolucao",
                    quantity=withdrawal.quantity,
                    balance_after=item.stock,
                    reason="Exclusao de retirada",
                    created_by=request.session.get("user"),
                )
            )
        db.delete(withdrawal)
        db.commit()
    return RedirectResponse(url="/historico", status_code=303)


@router.get("/relatorios/pdf")
def export_pdf(
    request: Request,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    technician_id: int | None = Query(None),
    item_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> Response:
    redirect = require_login(request)
    if redirect:
        return redirect

    rows = db.execute(_summary_query(start_date, end_date, technician_id, item_id)).all()
    content = build_pdf_report(rows, start_date, end_date)
    return StreamingResponse(
        content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=relatorio-cestacontrol.pdf"},
    )


@router.get("/relatorios/excel")
def export_excel(
    request: Request,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    technician_id: int | None = Query(None),
    item_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> Response:
    redirect = require_login(request)
    if redirect:
        return redirect

    rows = db.execute(_summary_query(start_date, end_date, technician_id, item_id)).all()
    content = build_excel_report(rows, start_date, end_date)
    return StreamingResponse(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=relatorio-cestacontrol.xlsx"},
    )
