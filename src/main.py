from typing import Annotated, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlmodel import Session, select
from datetime import date, datetime
import os
import uvicorn

# TUS IMPORTS (Ajustados a tus archivos reales)
from models.videojuego import Videojuego, VideojuegoCreateDTO, map_create_videojuego_to_videojuego
from data.db import init_db, get_session
from data.repository_videojuego import RepositoryVideojuego
from routers.api_videojuego_routers import router as api_videojuego_router

@asynccontextmanager
async def lifespan(application: FastAPI):
    # NOTA: init_db() borra y crea la base de datos al arrancar. 
    # Si quieres persistencia real tras reiniciar, comenta la línea de dentro de init_db que hace drop_all
    init_db() 
    yield

SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI(lifespan=lifespan)

# --- 1. CONFIGURACIÓN DE RUTAS (Vital para Docker) ---
script_dir = os.path.dirname(__file__)
static_abs_path = os.path.join(script_dir, "static")
templates_abs_path = os.path.join(script_dir, "templates")

app.mount("/static", StaticFiles(directory=static_abs_path), name="static")
templates = Jinja2Templates(directory=templates_abs_path)

app.include_router(api_videojuego_router)


# --- 2. RUTAS WEB ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/videojuegos", response_class=HTMLResponse)
async def get_videojuegos(request: Request, session: SessionDep):
    repo = RepositoryVideojuego(session)
    videojuegos = repo.get_all()
    # CORREGIDO: Se llama 'lista.html'
    return templates.TemplateResponse("videojuegos/lista.html", {"request": request, "videojuegos": videojuegos})


# --- 3. RUTAS DE BÚSQUEDA ---
@app.get("/videojuegos/buscar/titulo/", response_class=HTMLResponse)
async def get_videojuegos_by_titulo(request: Request, session: SessionDep, titulo: str = ""):
    repo = RepositoryVideojuego(session)
    videojuegos = repo.get_by_titulo(titulo) if titulo else []
    return templates.TemplateResponse("videojuegos/lista.html", {
        "request": request, "videojuegos": videojuegos, "titulo_buscado": titulo
    })

@app.get("/videojuegos/buscar/desarrolladora/", response_class=HTMLResponse)
async def get_videojuegos_by_desarrolladora(request: Request, session: SessionDep, desarrolladora: str = ""):
    repo = RepositoryVideojuego(session)
    videojuegos = repo.get_by_desarrolladora(desarrolladora) if desarrolladora else []
    return templates.TemplateResponse("videojuegos/lista.html", {
        "request": request, "videojuegos": videojuegos, "desarrolladora_buscando": desarrolladora
    })   

@app.get("/videojuegos/buscar/multijugador/", response_class=HTMLResponse)
async def get_videojuegos_by_multijugador(request: Request, session: SessionDep, multijugador: str = ""):
    repo = RepositoryVideojuego(session)
    videojuegos = []
    # Tu HTML manda "true"/"false" como texto
    if multijugador == "true":
        videojuegos = repo.get_multijugador(True)
    elif multijugador == "false":
        videojuegos = repo.get_multijugador(False)
    else:
        videojuegos = repo.get_all()
        
    return templates.TemplateResponse("videojuegos/lista.html", {
        "request": request, "videojuegos": videojuegos, "multijugador_buscando": multijugador
    })

@app.get("/videojuegos/buscar/fechas/", response_class=HTMLResponse)
async def get_videojuegos_by_intervalo_fecha_lanzamiento(request: Request, session: SessionDep, fecha_inicio: str = "", fecha_final: str = ""):
    repo = RepositoryVideojuego(session)
    juegos = []
    if fecha_inicio and fecha_final:
        try:
            juegos = repo.get_by_intervalo_fecha_lanzamiento(date.fromisoformat(fecha_inicio), date.fromisoformat(fecha_final))
        except ValueError:
            pass 
    return templates.TemplateResponse("videojuegos/lista.html", {
        "request": request, "videojuegos": juegos, "fecha_inicio_buscando": fecha_inicio, "fecha_final_buscando": fecha_final
    })


# --- 4. CREAR VIDEOJUEGO (GET y POST) ---

# ESTA ES LA RUTA QUE TE FALTABA PARA VER EL FORMULARIO
@app.get("/videojuegos/new", response_class=HTMLResponse)
async def form_nuevo_videojuego(request: Request):
    # Pasamos objeto vacío para evitar error de Jinja
    v_vacio = Videojuego(titulo="", desarrolladora="", fecha_lanzamiento=None, es_multijugador=False)
    # CORREGIDO: Se llama 'form.html'
    return templates.TemplateResponse("videojuegos/form.html", {"request": request, "videojuego": v_vacio})

@app.post("/videojuegos/new", response_class=HTMLResponse)
async def create_videojuego_web(request: Request, session: SessionDep):
    form_data = await request.form()
    
    titulo = str(form_data.get("titulo", "")).strip()
    desarrolladora = str(form_data.get("desarrolladora", "")).strip()
    fecha_str = form_data.get("fecha_lanzamiento")
    # Checkbox logic: si no está marcado, es None
    es_multi = form_data.get("es_multijugador") is not None

    error_msg = None
    if not titulo or not desarrolladora:
        error_msg = "Título y desarrolladora obligatorios."

    fecha_obj = None
    if fecha_str:
        try:
            fecha_obj = datetime.strptime(str(fecha_str), "%Y-%m-%d").date()
        except ValueError:
            error_msg = "Fecha inválida."

    # Si hay error, devolvemos el formulario con el mensaje
    if error_msg:
        v_error = Videojuego(titulo=titulo, desarrolladora=desarrolladora, fecha_lanzamiento=fecha_obj, es_multijugador=es_multi)
        # CORREGIDO: 'form.html'
        return templates.TemplateResponse("videojuegos/form.html", {"request": request, "videojuego": v_error, "error": error_msg})
    
    # Crear y guardar
    try:
        dto = VideojuegoCreateDTO(titulo=titulo, desarrolladora=desarrolladora, fecha_lanzamiento=fecha_obj, es_multijugador=es_multi)
        repo = RepositoryVideojuego(session)
        repo.create(map_create_videojuego_to_videojuego(dto))
        return RedirectResponse(url="/videojuegos", status_code=303)
    except Exception as e:
        v_error = Videojuego(titulo=titulo, desarrolladora=desarrolladora, fecha_lanzamiento=fecha_obj, es_multijugador=es_multi)
        return templates.TemplateResponse("videojuegos/form.html", {"request": request, "videojuego": v_error, "error": str(e)})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)