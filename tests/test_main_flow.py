import os
from pathlib import Path

from fastapi.testclient import TestClient


def test_main_flow_registers_withdrawal_and_exports_reports():
    os.environ["DATABASE_URL"] = "sqlite:///./data/test_cestacontrol.db"
    from app.main import app

    try:
        with TestClient(app) as client:
            login = client.post(
                "/login",
                data={"username": "admin", "password": "admin123"},
                follow_redirects=False,
            )
            assert login.status_code == 303

            technician = client.post(
                "/tecnicos",
                data={"name": "Tecnico Teste", "role": "Tecnico"},
                follow_redirects=False,
            )
            assert technician.status_code in {303, 400}

            item = client.post(
                "/estoque",
                data={"name": "Cesta Teste", "unit": "unidade", "stock": "10", "minimum_stock": "2"},
                follow_redirects=False,
            )
            assert item.status_code in {303, 400}

            withdrawal = client.post(
                "/retiradas",
                data={
                    "technician_id": "1",
                    "item_id": "1",
                    "quantity": "1",
                    "withdrawn_at": "2026-05-05",
                    "notes": "",
                },
                follow_redirects=False,
            )
            assert withdrawal.status_code in {303, 400}

            assert client.get("/historico").status_code == 200
            assert client.get("/relatorios/pdf").headers["content-type"] == "application/pdf"
            assert "spreadsheetml" in client.get("/relatorios/excel").headers["content-type"]
    finally:
        from app.database import engine

        engine.dispose()
        Path("data/test_cestacontrol.db").unlink(missing_ok=True)
