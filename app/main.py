from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes.routes import router as routes_router
from app.services.search import router as search_router
from app.routes import customers
from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_methods=["*"],          
    allow_headers=["*"],
)
app.include_router(routes_router)
app.include_router(search_router)
app.include_router(customers.router)
