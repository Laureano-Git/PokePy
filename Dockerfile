# 1. Imagen base ligera oficial de Python
FROM python:3.11-slim

# 2. Evita que Python genere archivos .pyc y fuerza la salida de logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar e instalar dependencias primero (aprovecha la caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código del bot al contenedor
COPY . .

# 6. Crear un usuario no-root por seguridad
RUN useradd -m discorduser && chown -R discorduser:discorduser /app
USER discorduser

# 7. Comando para ejecutar el bot (reemplaza 'main.py' si tu archivo se llama 'bot.py')
CMD ["python", "main.py"]