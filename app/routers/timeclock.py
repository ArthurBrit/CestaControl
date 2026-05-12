from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.database import get_db
from app.models import TimeRecord, User
from app.routers.deps import require_role


router = APIRouter(prefix="/ponto", tags=["ponto"])
templates = Jinja2Templates(directory="app/templates")

RECORD_TYPES = {
    "entrada": "Entrada",
    "inicio_intervalo": "Inicio do intervalo",
    "fim_intervalo": "Fim do intervalo",
    "saida": "Saida",
    "ajuste": "Ajuste manual",
}


@router.get("", response_class=HTMLResponse)
def timeclock_page(
    request: Request,
    selected_date: date | None = Query(None),
    user_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> Response:
    redirect = require_role(request, {"admin"})
    if redirect:
        return redirect

    selected_date = selected_date or date.today()
    start_at = datetime.combine(selected_date, time.min)
    end_at = datetime.combine(selected_date, time.max)

    stmt = (
        select(TimeRecord)
        .join(TimeRecord.user)
        .where(TimeRecord.recorded_at >= start_at, TimeRecord.recorded_at <= end_at)
        .order_by(TimeRecord.recorded_at.desc(), TimeRecord.id.desc())
    )
    if user_id:
        stmt = stmt.where(TimeRecord.user_id == user_id)

    users = db.scalars(select(User).where(User.active.is_(True)).order_by(User.full_name.asc())).all()
    records = db.scalars(stmt).all()
    return templates.TemplateResponse(
        request,
        "timeclock.html",
        {
            "users": users,
            "records": records,
            "record_types": RECORD_TYPES,
            "today": datetime.now().strftime("%Y-%m-%dT%H:%M"),
            "filters": {"selected_date": selected_date, "user_id": user_id},
        },
    )


@router.post("")
def create_time_record(
    request: Request,
    user_id: int = Form(...),
    record_type: str = Form(...),
    recorded_at: datetime = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    redirect = require_role(request, {"admin"})
    if redirect:
        return redirect

    user = db.get(User, user_id)
    if user and record_type in RECORD_TYPES:
        db.add(
            TimeRecord(
                user_id=user_id,
                record_type=record_type,
                recorded_at=recorded_at,
                notes=notes.strip() or None,
                created_by=request.session.get("user"),
            )
        )
        db.commit()

    return RedirectResponse(url=f"/ponto?selected_date={recorded_at.date().isoformat()}&user_id={user_id}", status_code=303)


@router.post("/{record_id}/excluir")
def delete_time_record(record_id: int, request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    redirect = require_role(request, {"admin"})
    if redirect:
        return redirect

    record = db.get(TimeRecord, record_id)
    redirect_date = date.today()
    if record:
        redirect_date = record.recorded_at.date()
        db.delete(record)
        db.commit()
    return RedirectResponse(url=f"/ponto?selected_date={redirect_date.isoformat()}", status_code=303)
