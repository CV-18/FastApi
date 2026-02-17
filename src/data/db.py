from models.videojuego import Videojuego
from datetime import date
from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

db_user:str = os.getenv("DB_USER", "carlos")
db_password: str = os.getenv("DB_PASSWORD", "1234")
db_server: str = os.getenv("DB_SERVER", "localhost")
db_port: int = int(os.getenv("DB_PORT", 3306))
db_name: str = os.getenv("DB_NAME", "videojuegos_db")

DATABASE_URL = f"mysql+pymysql://{db_user}:{db_password}@{db_server}:{db_port}/{db_name}"

engine = create_engine(os.getenv("DB_URL", DATABASE_URL), echo=True)

def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Videojuego(titulo="The Legend of Zelda: Breath of the Wild", desarrolladora="Nintendo", fecha_lanzamiento=date.fromisoformat("2017-03-03"), es_multijugador=False))
        session.add(Videojuego(titulo="Minecraft", desarrolladora="Mojang Studios", fecha_lanzamiento=date.fromisoformat("2011-11-18"), es_multijugador=True))
        session.add(Videojuego(titulo="Among Us", desarrolladora="InnerSloth", fecha_lanzamiento=date.fromisoformat("2018-06-15"), es_multijugador=True))
        session.add(Videojuego(titulo="The Witcher 3: Wild Hunt", desarrolladora="CD Projekt Red", fecha_lanzamiento=date.fromisoformat("2015-05-19"), es_multijugador=False))
        session.commit()
        


