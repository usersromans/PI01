# Sistema de Recomendación y API con FastAPI

Bienvenido al repositorio del Sistema de Recomendación y API desarrollado con FastAPI. Este proyecto ofrece una solución integral para la recomendación de videojuegos basada en análisis de reseñas y preferencias de usuarios, aprovechando técnicas avanzadas de procesamiento de datos y algoritmos de recomendación.

## Características Principales

- **Análisis Detallado por Desarrollador**: Obtén datos agregados sobre juegos por desarrollador, incluyendo la cantidad de ítems y el porcentaje de contenido gratuito.
- **Información Personalizada para Usuarios**: Accede a un resumen del gasto total, porcentaje de recomendaciones y cantidad de ítems por usuario.
- **Recomendaciones de Juegos**: Utiliza modelos de recomendación ítem-ítem y usuario-usuario para descubrir juegos similares o recomendados.
- **Insights por Género y Desarrollador**: Explora los géneros más populares y los desarrolladores con las mejores reseñas.
- **Documentación Interactiva**: FastAPI proporciona una documentación automática e interactiva para explorar todos los endpoints disponibles.

## Tecnologías Utilizadas

- **FastAPI**: Para la creación de endpoints RESTful de alta eficiencia.
- **Pandas**: Para el manejo y procesamiento de datos.
- **Scikit-learn**: Para calcular la similitud de coseno en los modelos de recomendación.
- **Uvicorn**: Como servidor ASGI para servir la aplicación.

## Despliegue

Este proyecto está desplegado y puede ser accedido en [https://pi01-usersromans1.onrender.com/docs](https://pi01-usersromans1.onrender.com/docs), donde encontrarás la documentación interactiva generada por FastAPI.

## Instalación Local

Para ejecutar este proyecto localmente, sigue estos pasos:

1. Clona el repositorio:
git clone https://github.com/usersromans/PI01.git

2. Instala las dependencias:
pip install fastapi uvicorn pandas scikit-learn

3. Inicia el servidor:
uvicorn main:app --reload


## Uso

Una vez que el servidor está corriendo, puedes explorar los endpoints disponibles a través de la documentación interactiva de FastAPI en `/docs`.

## Video Demostrativo

Para una guía detallada sobre cómo utilizar este sistema, por favor, visita nuestro video explicativo en YouTube: [Enlace al Video](<URL_DEL_VIDEO>).

## Contribuciones

Las contribuciones son siempre bienvenidas. Si tienes alguna sugerencia para mejorar este proyecto, no dudes en abrir un Pull Request o crear un Issue.

## Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, ver el archivo [LICENSE](LICENSE).

