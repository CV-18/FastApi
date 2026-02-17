from datetime import date
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

class Videojuego(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    titulo : str = Field(index=True, max_length=100)
    desarrolladora : str = Field(index=True, max_length=100)
    fecha_lanzamiento : date | None = Field(index = True)
    es_multijugador : bool = Field(default=False)


################################################################
class VideojuegoCreateDTO(BaseModel):
    titulo :str
    desarrolladora : str
    fecha_lanzamiento : date | None = None
    es_multijugador : bool 


################################################################
class VideojuegoUpdateDTO(BaseModel):
    titulo :str | None = None
    desarrolladora : str | None = None
    fecha_lanzamiento : date | None = None
    es_multijugador : bool | None = None

################################################################
class VideojuegoResponseDTO(BaseModel):
    titulo :str
    desarrolladora : str
    fecha_lanzamiento : date | None = None
    es_multijugador : bool    



########## MAPEO DE MODELOS A DTOs Y VICEVERSA ##########################
def map_create_videojuego_to_videojuego(create_dto: VideojuegoCreateDTO)-> Videojuego:
    return Videojuego(
        titulo= create_dto.titulo,
        desarrolladora = create_dto.desarrolladora,
        fecha_lanzamiento = create_dto.fecha_lanzamiento,
        es_multijugador= create_dto.es_multijugador
    )    



def map_update_videojuego_to_videojuego(juego: Videojuego, update_dto: VideojuegoUpdateDTO)-> Videojuego:
    if update_dto.titulo is not None:
        juego.titulo = update_dto.titulo
    if update_dto.desarrolladora is not None:
        juego.desarrolladora = update_dto.desarrolladora
    if update_dto.fecha_lanzamiento is not None:
        juego.fecha_lanzamiento = update_dto.fecha_lanzamiento
    if update_dto.es_multijugador is not None:
        juego.es_multijugador = update_dto.es_multijugador
    return juego

def map_videojuego_to_response_dto(videojuego: Videojuego)-> VideojuegoResponseDTO:
    return VideojuegoResponseDTO(
        titulo= videojuego.titulo,
        desarrolladora = videojuego.desarrolladora,
        fecha_lanzamiento = videojuego.fecha_lanzamiento,
        es_multijugador= videojuego.es_multijugador
    )