from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.services.quote import router as qoute_router
from app.services.invoice import router as invoice_router
from app.database import engine, Base
from app.routes.routes import router as routes_router
from app.services.search import router as search_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

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
app.include_router(qoute_router)
app.include_router(invoice_router)
app.include_router(routes_router)
app.include_router(search_router)
