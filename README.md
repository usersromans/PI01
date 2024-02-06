# PI1_MLOps

## Descripción
Este proyecto implementa una API con FastAPI para proporcionar datos y análisis sobre juegos, desarrolladores y usuarios. Incluye funcionalidades como el análisis de sentimientos de reseñas de usuarios y recomendaciones personalizadas basadas en datos históricos.

## Características
- Desarrollado con FastAPI.
- Análisis de sentimientos en reseñas de juegos.
- Información detallada sobre juegos, desarrolladores, y usuarios.
- Desplegado en Render.

## Instalación

Para clonar e instalar las dependencias del proyecto, sigue estos pasos:

git clone https://tu-repositorio-aqui.git
cd PI1_MLOps
pip install -r requirements.txt


## Uso

Para ejecutar la aplicación localmente:

uvicorn main:app --reload


Navega a `http://localhost:8000` para acceder a la documentación de la API generada por Swagger UI.

## Endpoints

### `/developer/{developer_name}`

Devuelve la cantidad de items y el porcentaje de contenido gratuito por año para un desarrollador específico.

### `/userdata/{user_id}`

Muestra la cantidad de dinero gastado, el porcentaje de recomendación, y la cantidad de items para un usuario específico.

### `/user_for_genre/{genre}`

Identifica al usuario con más horas jugadas en un género específico y detalla las horas jugadas por año de lanzamiento.

### `/best_developer_year/{year}`

Lista el top 3 de desarrolladores con juegos más recomendados por los usuarios para un año específico.

### `/developer_reviews_analysis/{developer_name}`

Analiza las reseñas de juegos de un desarrollador específico, contando reseñas positivas y negativas.

## Despliegue

Para desplegar en Render:

1. Regístrate y conecta tu repositorio en Render.
2. Sigue las instrucciones para configurar el servicio web.
3. Usa la URL proporcionada por Render para acceder a tu API en producción.

## Contribuir

Para contribuir al proyecto:

- Haz un fork del repositorio.
- Crea una rama para tu nueva característica.
- Realiza tus cambios y haz commit.
- Envía un Pull Request desde tu fork.

