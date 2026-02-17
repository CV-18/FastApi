from models.videojuego import Videojuego
from sqlmodel import Session, col, select
from datetime import date

class RepositoryVideojuego:
    def __init__(self, session):
        self.session = session


    def get_all(self)-> list[Videojuego]:
        videojuegos = list(self.session.exec(select(Videojuego)).all())
        return videojuegos
    

    def get_by_id(self, videojuego_id: int)-> Videojuego |None:
        videojuego = self.session.get(Videojuego, videojuego_id)
        return videojuego
    
    def get_by_titulo(self, titulo: str)-> list[Videojuego]:
        videojuegos = list(self.session.exec(select(Videojuego).where(col(Videojuego.titulo).ilike(f"%{titulo}%"))).all())
        return videojuegos
    

    def get_by_desarrolladora(self, desarrolladora: str)-> list[Videojuego]:
        videojuegos = list(self.session.exec(select(Videojuego).where(col(Videojuego.desarrolladora).ilike(f"%{desarrolladora}%"))).all())
        return videojuegos
    
    def get_by_intervalo_fecha_lanzamiento(self, fecha_inicio: date, fecha_final: date)-> list[Videojuego]:
        Videojuego.fecha_lanzamiento = date.fromisoformat("yyyy-mm-dd")
        videojuegos = list(self.session.exec(select(Videojuego).where(Videojuego.fecha_lanzamiento >= fecha_inicio and Videojuego.fecha_lanzamiento <= fecha_final)).all())
        return videojuegos
    

    def get_multijugador(self, multijugador : bool)-> list[Videojuego]:
        multijugador = True
        videojuegos = list(self.session.exec(select(Videojuego).where(Videojuego.es_multijugador == multijugador)).all())
        return videojuegos
    

    def get_single_multijugador(self, multijugador : bool)-> list[Videojuego]:
        multijugador = False
        videojuego = list(self.session.exec(select(Videojuego).where(Videojuego.es_multijugador == multijugador)).all())
        return videojuego
    

    def create(self, videojuego: Videojuego)-> Videojuego:
        self.session.add(videojuego)
        self.session.commit()
        self.session.refresh(videojuego)
        return videojuego
    

    def update(self, videojuego_id: int, videojuego_data: dict)-> Videojuego:
        videojuego = self.get_by_id(videojuego_id)
        if videojuego is None:
            raise ValueError(f"Videojuego con id {videojuego_id} no encontrado")
        for key,value in videojuego_data.items():
            setattr(videojuego, key, value)
        self.session.commit()
        self.session.refresh(videojuego)
        return videojuego
    


    def delete(self, videojuego_id: int)-> None:
        videojuego = self.get_by_id(videojuego_id)
        if videojuego is None:
            raise ValueError(f"Videojuego con id {videojuego_id} no encontrado")
        self.session.delete(videojuego)
        self.session.commit()
