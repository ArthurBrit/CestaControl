from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import InventoryItem, Technician, Withdrawal
from app.routers.deps import require_login


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)) -> Response:
    redirect = require_login(request)
    if redirect:
        return redirect

    total_stock = db.scalar(select(func.coalesce(func.sum(InventoryItem.stock), 0))) or 0
    total_technicians = db.scalar(select(func.count()).select_from(Technician).where(Technician.active.is_(True))) or 0
    total_withdrawals = db.scalar(select(func.coalesce(func.sum(Withdrawal.quantity), 0))) or 0
    low_stock_items = db.scalars(
        select(InventoryItem)
        .where(InventoryItem.active.is_(True), InventoryItem.stock <= InventoryItem.minimum_stock)
        .order_by(InventoryItem.stock.asc(), InventoryItem.name.asc())
    ).all()
    recent_withdrawals = db.scalars(
        select(Withdrawal).join(Withdrawal.technician).join(Withdrawal.item).order_by(Withdrawal.withdrawn_at.desc(), Withdrawal.id.desc()).limit(8)
    ).all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "total_stock": total_stock,
            "total_technicians": total_technicians,
            "total_withdrawals": total_withdrawals,
            "low_stock_items": low_stock_items,
            "recent_withdrawals": recent_withdrawals,
        },
    )
