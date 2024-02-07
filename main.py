from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Carga de datos desde archivos parquet para cada endpoint
file_path_1 = './data/dataset_endpoint_1.parquet'
df1 = pd.read_parquet(file_path_1)

file_path_2 = 'data/dataset_endpoint_2.parquet'
df2 = pd.read_parquet(file_path_2)

file_path_3 = 'data/dataset_endpoint_3.parquet'
df3 = pd.read_parquet(file_path_3)

file_path_4 = 'data/dataset_endpoint_4.parquet'
df4 = pd.read_parquet(file_path_4)

file_path_5 = 'data/dataset_endpoint_5.parquet'
df5 = pd.read_parquet(file_path_5)

# Endpoint raíz: mensaje de bienvenida y cómo acceder a la documentación
@app.get("/")
async def root():
    return {"message": "Bienvenido a mi API FastAPI. Usa /docs para ver la documentación."}

# Endpoint 1: Información de desarrollador por nombre
@app.get("/developer/{developer_name}")
async def developer(developer_name: str):
    # Filtrado y agrupación de datos por desarrollador
    filtered_df = df1[df1['developer'].str.lower() == developer_name.lower()]
    grouped = filtered_df.groupby('release_anio').agg(
        total_items=('items_total', 'sum'),
        free_content_percentage=('items_free', lambda x: f"{(x.sum() / x.count() * 100):.2f}%")
    ).reset_index()
    response = grouped.to_dict(orient='records')
    return {"developer": developer_name, "data": response}

# Endpoint 2: Datos de usuario por ID de usuario
@app.get("/userdata/{user_id}")
async def userdata(user_id: str):
    # Filtrado y cálculos para usuario específico
    filtered_df = df2[df2['user_id'] == user_id]
    total_spent = filtered_df['cantidad total gastado'].sum()
    items_count = filtered_df['item_id'].nunique()
    percentage_of_recommendation = filtered_df.iloc[0]['percentage_true'] if not filtered_df.empty else "0%"
    response = {
        "Usuario": user_id,
        "Dinero gastado": f"{total_spent} USD",
        "% de recomendación": percentage_of_recommendation,
        "Cantidad de items": items_count
    }
    return response

# Endpoint 3: Usuario con más horas jugadas por género
@app.get("/userforgebre/{genre}")
async def user_for_genre(genre: str):
    # Filtrado por género y cálculos de horas jugadas
    filtered_df = df3[df3['genres'].str.contains(genre, case=False)]
    user_hours = filtered_df.groupby('user_id')['playtime_forever'].sum().reset_index()
    top_user = user_hours.loc[user_hours['playtime_forever'].idxmax()]
    hours_per_year = filtered_df.groupby('release_anio')['playtime_forever'].sum().reset_index()
    response = {
        "Usuario con más horas jugadas para Género": genre,
        "user_id": top_user['user_id'],
        "Horas jugadas": hours_per_year.to_dict(orient='records')
    }
    return response

# Endpoint 4: Top 3 desarrolladores por año con más reseñas positivas
@app.get("/best_developer_year/{year}")
async def best_developer_year(year: int):
    # Filtrado por año y análisis de sentimiento
    filtered_df = df4[df4['release_anio'] == year]
    positive_reviews_df = filtered_df[filtered_df['sentiment_analysis'] == 2]
    developers_ranking = positive_reviews_df.groupby('developer').size().reset_index(name='positive_reviews_count')
    top_developers = developers_ranking.sort_values(by='positive_reviews_count', ascending=False).head(3)
    response = [{"Puesto {}: {}".format(i+1, dev['developer']): dev['positive_reviews_count']} for i, dev in enumerate(top_developers.to_dict(orient='records'))]
    return {"Año": year, "Top 3 desarrolladores": response}

# Endpoint 5: Análisis de reseñas de usuarios por desarrollador
@app.get("/developer_reviews_analysis/{developer_name}")
async def developer_reviews_analysis(developer_name: str):
    # Filtrado por nombre de desarrollador y conteo de análisis de sentimiento
    filtered_df = df5[df5['developer'].str.lower() == developer_name.lower()]
    sentiment_counts = filtered_df['sentiment_analysis'].value_counts().to_dict()
    response = {
        'Negative': sentiment_counts.get(0, 0),
        'Positive': sentiment_counts.get(2, 0)
    }
    return {developer_name: response}
