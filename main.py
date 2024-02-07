from fastapi import FastAPI
import pandas as pd
import zipfile
import os
import shutil
import numpy as np

app = FastAPI()

# Directorio temporal para extraer los archivos
temp_dir = './data/temp'

# Asegurarse de que el directorio temporal existe
os.makedirs(temp_dir, exist_ok=True)

# Función para extraer archivos CSV de un archi vo ZIP y cargarlos en un DataFrame
def extract_csv_from_zip(zip_path, temp_dir, csv_file_name):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    csv_path = os.path.join(temp_dir, csv_file_name)
    df = pd.read_csv(csv_path)
    # Opcional: eliminar el archivo CSV después de cargarlo para ahorrar espacio
    os.remove(csv_path)
    return df

# Función para limpiar el directorio temporal después de cargar todos los archivos necesarios
def clean_up_temp_dir():
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

# Rutas a los archivos ZIP
zip_path_plays = './data/data_plays.zip'
zip_path_reviews = './data/data_reviews.zip'

# Carga inicial de DataFrames con los archivos descomprimidos
data_plays_df = extract_csv_from_zip(zip_path_plays, temp_dir, 'data_plays.csv')
data_reviews_df = extract_csv_from_zip(zip_path_reviews, temp_dir, 'data_reviews.csv')

# Limpieza del directorio temporal después de cargar los DataFrames
clean_up_temp_dir()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/developer/{developer_name}")
async def get_developer_stats(developer_name: str):
    # Filtrar df por el desarrollador especificado
    df_filtrado = data_plays_df[data_plays_df['publisher'] == developer_name]

    # Asegurarse de que 'year' sea un entero para agrupar correctamente
    df_filtrado['year'] = df_filtrado['year'].astype(int)

    # Agrupar por año y calcular la cantidad de ítems y el porcentaje de contenido gratuito
    stats_por_año = df_filtrado.groupby('year').apply(
        lambda x: {
            "Cantidad de Items": len(x),
            # Calcular el porcentaje de contenido gratuito basado en la columna 'price'
            "Contenido Free": f"{(x['price'].isin(['Free', 'Free to Play'])).mean() * 100:.2f}%"
        }
    ).reset_index(name='Stats')

    return {"developer": developer_name, "stats": stats_por_año.to_dict(orient='records')}




@app.get("/userdata/{user_id}")
async def get_user_data(user_id: str):
    # Filtrar las reseñas por user_id
    df_reviews_filtrado = data_reviews_df[data_reviews_df['user_id'] == user_id].copy()

    # Convertir valores de 'recommend' de string a numérico (1 para 'True', 0 para 'False')
    df_reviews_filtrado['recommend_numeric'] = df_reviews_filtrado['recommend'].map({'True': 1, 'False': 0}).fillna(0)

    # Calcular el porcentaje de recomendaciones
    recomendaciones = df_reviews_filtrado['recommend_numeric'].mean() * 100

    # Filtrar los ítems jugados/comprados por el user_id
    df_plays_filtrado = data_plays_df[data_plays_df['user_id'] == user_id].copy()

    # Asegurar que la columna 'price' se trate correctamente como numérica donde sea posible
    # Se asume que 'price' contiene tanto valores numéricos como las cadenas 'Free' y 'Free to Play'
    df_plays_filtrado['price'] = pd.to_numeric(df_plays_filtrado['price'], errors='coerce').fillna(0)

    # Calcular la cantidad de dinero gastado
    dinero_gastado = df_plays_filtrado['price'].sum()

    # Contar la cantidad de ítems
    cantidad_items = len(df_plays_filtrado)

    return {
        "user_id": user_id,
        "Dinero gastado": f"${dinero_gastado:.2f}",
        "% de recomendación": f"{recomendaciones:.2f}%",
        "Cantidad de ítems": cantidad_items
    }



@app.get("/user_for_genre/{genre}")
async def get_user_for_genre(genre: str):
    # Asumiendo que 'genre' es una de las columnas dummy en 'data_plays_df'
    # y que 'year' representa el año de lanzamiento del juego.
    
    # Filtrar juegos por género
    df_genre = data_plays_df[data_plays_df[genre] == 1]
    
    # Agrupar por 'user_id' y sumar 'playtime_forever' para encontrar el usuario con más horas jugadas
    top_user = df_genre.groupby('user_id')['playtime_forever'].sum().idxmax()
    playtime_top_user = df_genre.groupby('user_id')['playtime_forever'].sum().max()

    # Agrupar por 'year' y sumar 'playtime_forever' para obtener horas jugadas por año
    hours_per_year = df_genre.groupby('year')['playtime_forever'].sum().reset_index()

     # Convertir el resultado a tipo Python nativo
    playtime_top_user = playtime_top_user.item()  # Si playtime_top_user es un numpy.int64

    # Asegúrate de que todos los valores en horas_per_year sean también de tipo Python nativo
    # Por ejemplo, si 'hours_per_year' es un DataFrame:
    hours_per_year = hours_per_year.applymap(lambda x: x.item() if isinstance(x, np.generic) else x)

    return {
        "Usuario con más horas jugadas para género": genre,
        "user_id": top_user,
        "Total horas jugadas por el top usuario": playtime_top_user,
        "Horas jugadas por año": hours_per_year.to_dict(orient='records')
    }






@app.get("/best_developer_year/{year}")
async def get_best_developer_year(year: int):
    # Filtrar los reviews por el año especificado
    df_reviews_year = data_reviews_df[data_reviews_df['year'] == year]

    if df_reviews_year.empty:
        return {"Top Developers for Year": year, "Developers": "No data for this year"}

    # Filtrar por recomendaciones positivas
    df_positive = df_reviews_year[df_reviews_year['recommend'] == True]

    if df_positive.empty:
        return {"Top Developers for Year": year, "Developers": "No positive recommendations for this year"}

    # Agrupar por publisher y contar el número de recomendaciones positivas
    developer_counts = df_positive.groupby('publisher').size().reset_index(name='positive_recommendations')

    # Ordenar por el número de recomendaciones positivas y tomar los top 3
    top_developers = developer_counts.sort_values(by='positive_recommendations', ascending=False).head(3)

    # Convertir el resultado a una lista de diccionarios para la respuesta
    top_developers_list = top_developers.to_dict(orient='records')

    return {"Top Developers for Year": year, "Developers": top_developers_list}



@app.get("/developer_reviews_analysis/{developer_name}")
async def developer_reviews_analysis(developer_name: str):
    # Filtrar data_reviews_df por developer_name
    df_filtered = data_reviews_df[data_reviews_df['publisher'] == developer_name]
    
    if df_filtered.empty:
        return {"Error": "No data found for the specified developer."}

    # Calcular el número de reseñas positivas y negativas
    # Asumiendo que 'sentiment_analysis' ya está calculado como 0: negativo, 1: neutral, 2: positivo
    positive_reviews = df_filtered[df_filtered['sentiment_analysis'] == 2].shape[0]
    negative_reviews = df_filtered[df_filtered['sentiment_analysis'] == 0].shape[0]

    # Crear la respuesta
    response = {
        developer_name: {
            "Positive": positive_reviews,
            "Negative": negative_reviews
        }
    }

    return response






