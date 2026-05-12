from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import InventoryItem, InventoryMovement
from app.routers.deps import require_login, require_role


router = APIRouter(prefix="/estoque", tags=["estoque"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def list_inventory(request: Request, db: Session = Depends(get_db)) -> Response:
    redirect = require_login(request)
    if redirect:
        return redirect

    items = db.scalars(select(InventoryItem).order_by(InventoryItem.active.desc(), InventoryItem.name.asc())).all()
    movements = db.scalars(
        select(InventoryMovement).join(InventoryMovement.item).order_by(InventoryMovement.created_at.desc(), InventoryMovement.id.desc()).limit(12)
    ).all()
    total_stock = sum(item.stock for item in items if item.active)
    low_stock_count = sum(1 for item in items if item.active and item.stock <= item.minimum_stock)
    return templates.TemplateResponse(
        request,
        "inventory.html",
        {"items": items, "movements": movements, "total_stock": total_stock, "low_stock_count": low_stock_count, "error": None},
    )


@router.post("")
def create_item(
    request: Request,
    name: str = Form(...),
    unit: str = Form("unidade"),
    category: str = Form("Geral"),
    location: str = Form("Almoxarifado"),
    stock: int = Form(0),
    minimum_stock: int = Form(0),
    db: Session = Depends(get_db),
) -> Response:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    item = InventoryItem(
        name=name.strip(),
        category=category.strip() or "Geral",
        unit=unit.strip() or "unidade",
        location=location.strip() or "Almoxarifado",
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
            {"items": items, "movements": [], "total_stock": 0, "low_stock_count": 0, "error": "Item ja cadastrado."},
            status_code=400,
        )
    if item.stock > 0:
        db.add(
            InventoryMovement(
                item_id=item.id,
                movement_type="cadastro",
                quantity=item.stock,
                balance_after=item.stock,
                reason="Estoque inicial",
                created_by=request.session.get("user"),
            )
        )
        db.commit()
    return RedirectResponse(url="/estoque", status_code=303)


@router.post("/{item_id}/entrada")
def add_stock(
    item_id: int,
    request: Request,
    quantity: int = Form(...),
    reason: str = Form("Entrada de estoque"),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    item = db.get(InventoryItem, item_id)
    if item and quantity > 0:
        item.stock += quantity
        db.add(
            InventoryMovement(
                item_id=item_id,
                movement_type="entrada",
                quantity=quantity,
                balance_after=item.stock,
                reason=reason.strip() or "Entrada de estoque",
                created_by=request.session.get("user"),
            )
        )
        db.commit()
    return RedirectResponse(url="/estoque", status_code=303)


@router.post("/{item_id}/ajustar")
def adjust_stock(
    item_id: int,
    request: Request,
    stock: int = Form(...),
    minimum_stock: int = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    item = db.get(InventoryItem, item_id)
    if item:
        previous_stock = item.stock
        item.stock = max(stock, 0)
        item.minimum_stock = max(minimum_stock, 0)
        if item.stock != previous_stock:
            db.add(
                InventoryMovement(
                    item_id=item_id,
                    movement_type="ajuste",
                    quantity=item.stock - previous_stock,
                    balance_after=item.stock,
                    reason="Ajuste manual",
                    created_by=request.session.get("user"),
                )
            )
        db.commit()
    return RedirectResponse(url="/estoque", status_code=303)


@router.post("/{item_id}/alternar")
def toggle_item(item_id: int, request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    redirect = require_role(request, {"admin", "almoxarifado"})
    if redirect:
        return redirect

    item = db.get(InventoryItem, item_id)
    if item:
        item.active = not item.active
        db.commit()
    return RedirectResponse(url="/estoque", status_code=303)
