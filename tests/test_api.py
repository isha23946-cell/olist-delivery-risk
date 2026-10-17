from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

VALID_ORDER = {
    "customer_state": "PB",
    "seller_state": "SP",
    "primary_category": "furniture_decor",
    "estimated_days": 20,
    "distance_km": 2192,
    "items_price": 78,
    "items_freight": 83.47,
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_kpis():
    r = client.get("/kpis")
    assert r.status_code == 200
    body = r.json()
    assert body["summary"]["delivered_orders"] == 96476
    assert 0.9 < body["summary"]["on_time_rate"] < 0.93
    assert len(body["by_state"]) == 10


def test_high_risk_sorted_and_limited():
    r = client.get("/high-risk?limit=5")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 5
    scores = [row["risk_score"] for row in rows]
    assert scores == sorted(scores, reverse=True)


def test_high_risk_state_filter():
    r = client.get("/high-risk?limit=10&state=sp")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) > 0
    assert all(row["customer_state"] == "SP" for row in rows)


def test_high_risk_rejects_bad_limit():
    assert client.get("/high-risk?limit=0").status_code == 422
    assert client.get("/high-risk?limit=101").status_code == 422


def test_predict_valid_order():
    r = client.post("/predict", json=VALID_ORDER)
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["risk_score"] <= 1
    assert isinstance(body["flagged"], bool)
    assert len(body["top_factors"]) == 5


def test_predict_state_is_case_insensitive():
    lower = dict(VALID_ORDER, customer_state="pb")
    a = client.post("/predict", json=VALID_ORDER).json()
    b = client.post("/predict", json=lower).json()
    assert a["risk_score"] == b["risk_score"]


def test_predict_rejects_bad_input():
    assert client.post("/predict", json=dict(VALID_ORDER, items_price=-5)).status_code == 422
    assert client.post("/predict", json=dict(VALID_ORDER, customer_state="XYZ")).status_code == 422
    missing = {k: v for k, v in VALID_ORDER.items() if k != "distance_km"}
    assert client.post("/predict", json=missing).status_code == 422
