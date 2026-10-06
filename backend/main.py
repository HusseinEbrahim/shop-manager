import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from database import engine, Base
import models       
from routers import products, sales, auth, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shop Manager API")

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(dashboard.router)

@app.get("/")
def home():
    return {"message": "Shop Manager API is running"}