# 1. Usamos una imagen base de Python ligera
FROM python:3.11-slim

# 2. Evitamos que Python genere archivos .pyc y activamos logs inmediatos
WORKDIR /app


# 4. Copiamos las dependencias e instalamos
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5. Copiamos todo el proyecto (incluye `models`, `templates`, `static`, `src`, ...)
COPY ./src:/app/sr

# 6. Exponemos el puerto 8000
EXPOSE 8000

# 7. Comando para ejecutar la aplicación con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
