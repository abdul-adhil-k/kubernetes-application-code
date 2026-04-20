from fastapi import APIRouter, HTTPException
from app.logger import get_logger

router = APIRouter()
logger = get_logger("app")

ITEMS = [
    {"id": 1, "name": "Apple"},
    {"id": 2, "name": "Banana"},
    {"id": 3, "name": "Cherry"},
]


@router.get("/")
def health():
    logger.info("Health check called")
    return {"status": "ok"}

@router.get("/owner")
def get_owner():
    logger.info("Owner endpoint called")
    return {"owner": "Your Name"}


@router.get("/items")
def list_items():
    logger.info("Listing all items")
    return {"items": ITEMS}


@router.get("/items/{item_id}")
def get_item(item_id: int):
    item = next((i for i in ITEMS if i["id"] == item_id), None)
    if not item:
        logger.warning("Item %s not found", item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info("Fetched item %s", item_id)
    return item


@router.get("/error")
def simulate_error():
    logger.error("Simulated error endpoint was called")
    raise HTTPException(status_code=500, detail="Intentional error")
