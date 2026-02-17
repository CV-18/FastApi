from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from sqlmodel import Session
from datetime import date

# Asegúrate de que las rutas de importación sean correctas según tu estructura de carpetas
from data.db import get_session
from data.repository_videojuego import RepositoryVideojuego
from models.videojuego import Videojuego, VideojuegoCreateDTO, VideojuegoUpdateDTO, VideojuegoResponseDTO
from models.videojuego import map_create_videojuego_to_videojuego, map_update_videojuego_to_videojuego, map_videojuego_to_response_dto

router = APIRouter(prefix="/api/videojuegos", tags=["videojuegos"])

SessionDep = Annotated[Session, Depends(get_session)]

# 1. GET ALL (Siempre primero)
@router.get("/", response_model=list[VideojuegoResponseDTO])
async def get_all_videojuegos(session: SessionDep):
    repo = RepositoryVideojuego(session)
    videojuegos = repo.get_all()
    return [map_videojuego_to_response_dto(juego) for juego in videojuegos]

# 2. RUTAS ESPECÍFICAS (Búsquedas) - Deben ir ANTES de /{videojuego_id}

@router.get("/buscar/titulo/{titulo}", response_model=list[VideojuegoResponseDTO])
async def get_videojuegos_by_titulo(titulo: str, session: SessionDep):
    repo = RepositoryVideojuego(session)
    videojuegos = repo.get_by_titulo(titulo)
    if not videojuegos:
        raise HTTPException(status_code=404, detail="No se encontraron videojuegos con ese título")
    return [map_videojuego_to_response_dto(juego) for juego in videojuegos]

@router.get("/buscar/desarrolladora/{desarrolladora}", response_model=list[VideojuegoResponseDTO])
async def get_videojuegos_by_desarrolladora(desarrolladora: str, session: SessionDep):
    repo = RepositoryVideojuego(session)
    videojuegos = repo.get_by_desarrolladora(desarrolladora)
    if not videojuegos:
        raise HTTPException(status_code=404, detail="No se encontraron videojuegos con esa desarrolladora")
    return [map_videojuego_to_response_dto(juego) for juego in videojuegos]

@router.get("/buscar/multijugador/{multijugador}", response_model=list[VideojuegoResponseDTO])
async def get_videojuegos_by_multijugador(multijugador: bool, session: SessionDep):
    repo = RepositoryVideojuego(session)
    # Nota: Asegúrate de que tu repositorio tenga este método (get_multijugador)
    videojuegos = repo.get_multijugador(multijugador)
    if not videojuegos:
        raise HTTPException(status_code=404, detail="No se encontraron videojuegos con esa característica")
    return [map_videojuego_to_response_dto(juego) for juego in videojuegos]

@router.get("/buscar/fechas/{fecha_inicio}/{fecha_final}", response_model=list[VideojuegoResponseDTO])
async def get_videojuegos_by_intervalo_fecha_lanzamiento(fecha_inicio: date, fecha_final: date, session: SessionDep):
    repo = RepositoryVideojuego(session)
    # FastAPI ya valida el formato YYYY-MM-DD automáticamente
    videojuegos = repo.get_by_intervalo_fecha_lanzamiento(fecha_inicio, fecha_final)
    if not videojuegos:
        raise HTTPException(status_code=404, detail="No se encontraron videojuegos en ese intervalo")
    return [map_videojuego_to_response_dto(juego) for juego in videojuegos]

# 3. CREAR (POST)
@router.post("/newVideojuego", response_model=VideojuegoResponseDTO, status_code=201)
async def create_new_videojuego(videojuego_create_DTO: VideojuegoCreateDTO, session: SessionDep):
    repo = RepositoryVideojuego(session)
    new_videojuego = map_create_videojuego_to_videojuego(videojuego_create_DTO)
    created_videojuego = repo.create(new_videojuego)
    return map_videojuego_to_response_dto(created_videojuego)

# 4. RUTA GENÉRICA POR ID (¡Siempre al final de los GET!)
@router.get("/{videojuego_id}", response_model=VideojuegoResponseDTO)
async def get_videojuego(videojuego_id: int, session: SessionDep):
    repo = RepositoryVideojuego(session)
    videojuego = repo.get_by_id(videojuego_id)
    if videojuego is None:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado")
    return map_videojuego_to_response_dto(videojuego)

# 5. ACTUALIZAR Y BORRAR (PUT, PATCH, DELETE)
@router.put("/{videojuego_id}", response_model=VideojuegoResponseDTO)
async def update_videojuego(videojuego_id: int, videojuego_update_DTO: VideojuegoUpdateDTO, session: SessionDep):
    repo = RepositoryVideojuego(session)
    videojuego_encontrado = repo.get_by_id(videojuego_id)
    if not videojuego_encontrado:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado")
    datos_actualizados = videojuego_update_DTO.model_dump(exclude_unset=True)
    videojuego_guardado = repo.update(videojuego_id, datos_actualizados)
    return map_videojuego_to_response_dto(videojuego_guardado)

@router.delete("/{videojuego_id}", status_code=204)
async def delete_videojuego(videojuego_id: int, session: SessionDep):
    repo = RepositoryVideojuego(session)
    try:
        repo.delete(videojuego_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado")
    return None