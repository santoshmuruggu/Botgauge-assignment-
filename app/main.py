import os
import django
import traceback
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# -------------------------------------------------------------------
# Django setup
# -------------------------------------------------------------------
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "dbcore.dbcore.settings"
)
django.setup()

from dbcore.kvstore.models import Item

# -------------------------------------------------------------------
# FastAPI + Rate Limiter
# -------------------------------------------------------------------
app = FastAPI(title="Botgauge Key-Value API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )

# -------------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------------
class ItemCreate(BaseModel):
    key: str
    value: str

# -------------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------------

@app.post("/items/")
@limiter.limit("60/minute")
async def create_item(request: Request, data: ItemCreate):
    def db_op():
        if Item.objects.filter(key=data.key).exists():
            raise ValueError("Key exists")
        return Item.objects.create(key=data.key, value=data.value)

    try:
        item = await run_in_threadpool(db_op)
        return {"key": item.key, "value": item.value}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/items/{key}")
@limiter.limit("60/minute")
async def get_item(request: Request, key: str):
    def db_op():
        return Item.objects.get(key=key)

    try:
        item = await run_in_threadpool(db_op)
        return {"key": item.key, "value": item.value}
    except Item.DoesNotExist:
        raise HTTPException(status_code=404, detail="Key not found")


@app.put("/items/{key}")
@limiter.limit("60/minute")
async def update_item(request: Request, key: str, value: str):
    def db_op():
        item = Item.objects.get(key=key)
        item.value = value
        item.save()
        return item

    try:
        item = await run_in_threadpool(db_op)
        return {"key": item.key, "value": item.value}
    except Item.DoesNotExist:
        raise HTTPException(status_code=404, detail="Key not found")


@app.delete("/items/{key}")
@limiter.limit("60/minute")
async def delete_item(request: Request, key: str):
    def db_op():
        return Item.objects.filter(key=key).delete()

    deleted, _ = await run_in_threadpool(db_op)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Key not found")

    return {"message": "Deleted successfully"}


@app.get("/items/")
@limiter.limit("60/minute")
async def list_items(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    def db_op():
        qs = Item.objects.all().order_by("id")
        total = qs.count()

        start = (page - 1) * page_size
        end = start + page_size

        items = list(qs[start:end].values("key", "value"))

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "items": items,
        }

    return await run_in_threadpool(db_op)
