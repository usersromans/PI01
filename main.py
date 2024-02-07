from fastapi import FastAPI
import pandas as pd


app = FastAPI()



@app.get("/")
async def read_root():
    return {"Hello": "World"}


from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Asumimos que el dataframe está cargado globalmente para este ejemplo
file_path = './data/dataset_endpoint_1.parquet'
df = pd.read_parquet(file_path)

@app.get("/developer/{developer_name}")
async def developer(developer_name: str):
    # Filtra el dataframe por el nombre del desarrollador
    filtered_df = df[df['developer'].str.lower() == developer_name.lower()]
    
    # Agrupa por año de lanzamiento y calcula los totales y porcentajes
    grouped = filtered_df.groupby('release_anio').agg(
        total_items=('items_total', 'sum'),
        free_content_percentage=('items_free', lambda x: f"{(x.sum() / x.count() * 100):.2f}%")
    ).reset_index()
    
    # Construye la respuesta
    response = grouped.to_dict(orient='records')
    
    return {"developer": developer_name, "data": response}


# Asumiendo que la ruta al archivo está dentro de una subcarpeta "data" en el directorio actual
file_path = 'data/dataset_endpoint_2.parquet'
df2 = pd.read_parquet(file_path)

@app.get("/userdata/{user_id}")
async def userdata(user_id: str):
    # Filtra el dataframe por el ID de usuario
    filtered_df = df2[df2['user_id'] == user_id]
    
    # Calcula la cantidad total de dinero gastado
    total_spent = filtered_df['cantidad total gastado'].sum()
    
    # Calcula la cantidad de ítems
    items_count = filtered_df['item_id'].nunique()
    
    # Calcula el porcentaje de recomendaciones positivas (asumiendo que 'percentage_true' ya está en formato porcentual)
    # Si 'percentage_true' necesita ser calculado o transformado, este código necesitaría ajustes
    if not filtered_df.empty:
        percentage_of_recommendation = filtered_df.iloc[0]['percentage_true']  # Asume el mismo porcentaje para todas las filas
    else:
        percentage_of_recommendation = "0%"  # Asumimos 0% si no hay registros
    
    # Construye la respuesta
    response = {
        "Usuario": user_id,
        "Dinero gastado": f"{total_spent} USD",
        "% de recomendación": percentage_of_recommendation,
        "Cantidad de items": items_count
    }
    
    return response


# Cargamos el archivo parquet
file_path = 'data/dataset_endpoint_3.parquet'
df3 = pd.read_parquet(file_path)

@app.get("/userforgebre/{genre}")
async def user_for_genre(genre: str):
    # Filtra el dataframe por el género
    filtered_df = df3[df3['genres'].str.contains(genre, case=False)]
    
    # Encuentra el usuario con más horas jugadas en ese género
    user_hours = filtered_df.groupby('user_id')['playtime_forever'].sum().reset_index()
    top_user = user_hours.loc[user_hours['playtime_forever'].idxmax()]
    
    # Acumula horas jugadas por año de lanzamiento
    hours_per_year = filtered_df.groupby('release_anio')['playtime_forever'].sum().reset_index()
    hours_per_year_list = hours_per_year.to_dict(orient='records')
    
    # Construye la respuesta
    response = {
        "Usuario con más horas jugadas para Género": genre,
        "user_id": top_user['user_id'],
        "Horas jugadas": hours_per_year_list
    }
    
    return response

# Cargamos el archivo parquet
file_path = 'data/dataset_endpoint_4.parquet'
df4 = pd.read_parquet(file_path)

@app.get("/best_developer_year/{year}")
async def best_developer_year(year: int):
    # Filtra el dataframe por el año
    filtered_df = df4[df4['release_anio'] == year]
    
    # Filtra aún más por análisis de sentimiento positivo
    positive_reviews_df = filtered_df[filtered_df['sentiment_analysis'] == 2]
    
    # Agrupa por desarrollador y cuenta las reseñas positivas
    developers_ranking = positive_reviews_df.groupby('developer').size().reset_index(name='positive_reviews_count')
    
    # Ordena los desarrolladores por la cantidad de reseñas positivas y toma el top 3
    top_developers = developers_ranking.sort_values(by='positive_reviews_count', ascending=False).head(3)
    
    # Prepara la respuesta
    top_developers_list = top_developers.to_dict(orient='records')
    response = [{"Puesto {}: {}".format(i+1, dev['developer']): dev['positive_reviews_count']} for i, dev in enumerate(top_developers_list)]
    
    return {"Año": year, "Top 3 desarrolladores": response}



# Cargamos el archivo parquet
file_path = 'data/dataset_endpoint_5.parquet'
df5 = pd.read_parquet(file_path)

@app.get("/developer_reviews_analysis/{developer_name}")
async def developer_reviews_analysis(developer_name: str):
    # Filtra el dataframe por el nombre del desarrollador
    filtered_df = df5[df5['developer'].str.lower() == developer_name.lower()]
    
    # Cuenta los análisis de sentimiento positivos y negativos
    sentiment_counts = filtered_df['sentiment_analysis'].value_counts().to_dict()
    
    # Preparando la respuesta
    response = {
        'Negative': sentiment_counts.get(0, 0),
        'Positive': sentiment_counts.get(2, 0)
    }
    
    return {developer_name: response}