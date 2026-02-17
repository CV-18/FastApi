from typing import Annotated, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlmodel import Session, select

from models.videojuego import Videojuego, VideojuegoCreateDTO, VideojuegoUpdateDTO, VideojuegoResponseDTO, map_create_videojuego_to_videojuego
from data.db import init_db, get_session
from data.repository_videojuego import RepositoryVideojuego
from routers.api_videojuego_routers import router as api_videojuego_router
from datetime import date, datetime

import os
import uvicorn

@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    yield

SessionDep = Annotated[Session,Depends(get_session)]
app = FastAPI(lifespan=lifespan)


script_dir = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(script_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(script_dir, "templates"))

app.include_router(api_videojuego_router)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/videojuegos", response_class=HTMLResponse)
async def get_videojuegos(request:Request,session: SessionDep):
    repo = RepositoryVideojuego(session)
    videojuegos = repo.get_all()
    return templates.TemplateResponse("videojuegos/videojuegos.html", {"request": request, "videojuegos": videojuegos})


@app.get("/videojuegos/buscar/titulo/", response_class=HTMLResponse)
async def get_videojuegos_by_titulo(request:Request,  session:SessionDep,titulo:str = ""):
    repo = RepositoryVideojuego(session)
    if titulo:
        videojuegos = repo.get_by_titulo(titulo)
    else:
        videojuegos = []
    return templates.TemplateResponse("videojuegos/lista.html", {
        "request": request, 
        "videojuegos": videojuegos,
        "titulo_buscado": titulo
    })

@app.get("videojuegos/buscar/desarrolladora/", response_class=HTMLResponse)
async def get_videojuegos_by_desarrolladora(request:Request,session: SessionDep ,desarrolladora:str = ""):
    repo = RepositoryVideojuego(session)
    if desarrolladora:
        videojuegos = repo.get_by_desarrolladora(desarrolladora)
    else:
        videojuegos = []
    return templates.TemplateResponse("videojuegos/lista.html", {
        "request": request,
        "videojuegos": videojuegos,
        "desarrolladora_buscando": desarrolladora
    })   

@app.get("/videojuegos/buscar/multijugador/", response_class=HTMLResponse)
async def get_videojuegos_by_multijugador(request:Request, session: SessionDep, multijugador:str = ""):
    repo = RepositoryVideojuego(session)
    videojuegos = []
    filtro_multijugador : Optional[bool] = None
    if multijugador == "true":
        videojuegos = repo.get_multijugador(True)
    elif multijugador == "false":
        videojuegos = repo.get_multijugador(False)
    else:
        videojuegos = repo.get_all()
    return templates.TemplateResponse("videojuegos/lista.html", {
        "request": request,
        "videojuegos": videojuegos,
        "multijugador_buscando": multijugador
    })

@app.get("/videojuegos/buscar/fechas/", response_class=HTMLResponse)
async def get_videojuegos_by_intervalo_fecha_lanzamiento(request:Request, session:SessionDep, fecha_inicio:str="", fecha_final:str=""):
    repo = RepositoryVideojuego(session)
    if fecha_inicio and fecha_final:
        try:
            Videojuegos = repo.get_by_intervalo_fecha_lanzamiento(date.fromisoformat(fecha_inicio), date.fromisoformat(fecha_final))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha no válido. Use YYYY-MM-DD.")
    else:
        Videojuegos = []
    return templates.TemplateResponse("videojuegos/lista.html", {
        "request": request,
        "videojuegos": Videojuegos,
        "fecha_inicio_buscando": fecha_inicio,
        "fecha_final_buscando": fecha_final
    })

@app.post("/videojuegos/new", response_class=HTMLResponse)
async def create_videojuego_web(request: Request, session: SessionDep): # <--- Usamos SessionDep, no 'Session'
    
    form_data = await request.form()
    
    # 1. Recogida y Limpieza de datos
    titulo_form = str(form_data.get("titulo", "")).strip()
    desarrolladora_form = str(form_data.get("desarrolladora", "")).strip()
    fecha_str = form_data.get("fecha_lanzamiento") # Esto es un string "YYYY-MM-DD" o vacío
    
    # --- CORRECCIÓN DEL BOOLEANO ---
    # En un formulario, si el checkbox no se marca, get() devuelve None.
    # Si se marca, devuelve "on" (o lo que sea). 
    # Por tanto, simplemente comprobamos si no es None.
    es_multijugador_bool = form_data.get("es_multijugador") is not None

    # 2. Validaciones básicas
    error_msg = None
    if not titulo_form or not desarrolladora_form:
        error_msg = "Los campos título y desarrolladora son obligatorios."

    # --- CORRECCIÓN DE LA FECHA ---
    fecha_obj = None
    if fecha_str: # Solo intentamos convertir si hay texto
        try:
            # Usamos strptime que es más robusto para formatos de formulario
            fecha_obj = datetime.strptime(str(fecha_str), "%Y-%m-%d").date()
        except ValueError:
            error_msg = "La fecha de lanzamiento no es válida."

    # 3. Si hay error, devolvemos el formulario con los datos que metió el usuario y el error
    if error_msg:
        # Creamos un objeto temporal para repoblar el formulario
        v_con_error = Videojuego(
            titulo=titulo_form, 
            desarrolladora=desarrolladora_form, 
            fecha_lanzamiento=fecha_obj, 
            es_multijugador=es_multijugador_bool
        )
        return templates.TemplateResponse("videojuegos/album_form.html", {
            "request": request,
            "videojuego": v_con_error,
            "error": error_msg
        })
    
    # 4. Creación del DTO y Guardado
    # Aquí ya pasamos las variables limpias (bool y date), no las del form_data
    album_create = VideojuegoCreateDTO(
        titulo=titulo_form,
        desarrolladora=desarrolladora_form,
        fecha_lanzamiento=fecha_obj,    # Pasamos el objeto date (o None)
        es_multijugador=es_multijugador_bool # Pasamos el bool (True/False)
    )

    try:
        repo = RepositoryVideojuego(session) # Usamos la session inyectada
        videojuego = map_create_videojuego_to_videojuego(album_create)
        repo.create(videojuego)
        
        # Si todo va bien, REDIRIGIMOS a la lista
        return RedirectResponse(url="/videojuegos", status_code=303)
        
    except Exception as e:
        # Si falla la base de datos, mostramos el error en el formulario
        v_con_error = Videojuego(
            titulo=titulo_form, 
            desarrolladora=desarrolladora_form, 
            fecha_lanzamiento=fecha_obj, 
            es_multijugador=es_multijugador_bool
        )
        return templates.TemplateResponse("videojuegos/album_form.html", {
            "request": request,
            "videojuego": v_con_error,
            "error": f"Error interno: {str(e)}"
        })


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)
         

