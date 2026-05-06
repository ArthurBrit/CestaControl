from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import InventoryItem
from app.routers.deps import require_login


router = APIRouter(prefix="/estoque", tags=["estoque"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def list_inventory(request: Request, db: Session = Depends(get_db)) -> Response:
    redirect = require_login(request)
    if redirect:
        return redirect

    items = db.scalars(select(InventoryItem).order_by(InventoryItem.active.desc(), InventoryItem.name.asc())).all()
    return templates.TemplateResponse(request, "inventory.html", {"items": items, "error": None})


@router.post("")
def create_item(
    request: Request,
    name: str = Form(...),
    unit: str = Form("unidade"),
    stock: int = Form(0),
    minimum_stock: int = Form(0),
    db: Session = Depends(get_db),
) -> Response:
    redirect = require_login(request)
    if redirect:
        return redirect

    item = InventoryItem(
        name=name.strip(),
        unit=unit.strip() or "unidade",
        stock=max(stock, 0),
        minimum_stock=max(minimum_stock, 0),
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        items = db.scalars(select(InventoryItem).order_by(InventoryItem.name.asc())).all()
        return templates.TemplateResponse(
            request,
            "inventory.html",
            {"items": items, "error": "Item ja cadastrado."},
            status_code=400,
        )
    return RedirectResponse(url="/estoque", status_code=303)


@router.post("/{item_id}/ajustar")
def adjust_stock(
    item_id: int,
    request: Request,
    stock: int = Form(...),
    minimum_stock: int = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    redirect = require_login(request)
    if redirect:
        return redirect

    item = db.get(InventoryItem, item_id)
    if item:
        item.stock = max(stock, 0)
        item.minimum_stock = max(minimum_stock, 0)
        db.commit()
    return RedirectResponse(url="/estoque", status_code=303)


@router.post("/{item_id}/alternar")
def toggle_item(item_id: int, request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    redirect = require_login(request)
    if redirect:
        return redirect

    item = db.get(InventoryItem, item_id)
    if item:
        item.active = not item.active
        db.commit()
    return RedirectResponse(url="/estoque", status_code=303)
