from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Shop Manager API is running"}