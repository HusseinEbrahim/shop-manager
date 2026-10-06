from fastapi import FastAPI
from database import engine, Base
import models
from routers import products, sales
from routers import products, sales, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shop Manager API")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(sales.router)

@app.get("/")
def home():
    return {"message": "Shop Manager API is running"}