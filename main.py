from fastapi import FastAPI
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Inicializa la aplicación FastAPI
app = FastAPI()

# Carga de datos desde archivos parquet para cada funcionalidad de la API
file_paths = {
    'df1': './data/endpoint_1.parquet',
    'df2': 'data/endpoint_2.parquet',
    'df3': 'data/endpoint_3.parquet',
    'df4': 'data/endpoint_4.parquet',
    'df5': 'data/endpoint_5.parquet',
    'recomendacion': 'data/df_recomendacion.parquet'
}

# Lectura de los archivos parquet a DataFrames de pandas
dfs = {key: pd.read_parquet(path) for key, path in file_paths.items()}

# Creación de la matriz de valoraciones a partir del DataFrame de recomendaciones
ratings_matrix = dfs['recomendacion'].pivot_table(index='user_id', columns='item_name', values='rating').fillna(0)

# Cálculo de la similitud de coseno entre ítems y entre usuarios
item_similarity = cosine_similarity(ratings_matrix.T)
item_similarity_df = pd.DataFrame(item_similarity, index=ratings_matrix.columns, columns=ratings_matrix.columns)
user_similarity = cosine_similarity(ratings_matrix)
user_similarity_df = pd.DataFrame(user_similarity, index=ratings_matrix.index, columns=ratings_matrix.index)

# Función para recomendar ítems similares a un ítem dado
def recommend_items(item_name, similarity_data=item_similarity_df, n_items=5):
    """
    Dado el nombre de un ítem, encuentra ítems similares basados en valoraciones de usuarios.
    """
    similar_scores = similarity_data[item_name].sort_values(ascending=False)
    top_items = similar_scores[1:n_items+1].index
    return top_items

# Función para recomendar ítems a un usuario basándose en similitudes entre usuarios
def recommend_items_for_user(user_id, similarity_data=user_similarity_df, ratings_data=ratings_matrix, n_recommendations=5):
    """
    Dado un user_id, recomienda ítems que usuarios similares han valorado positivamente.
    """
    user_similarities = similarity_data[user_id].drop(user_id)
    most_similar_users = user_similarities.sort_values(ascending=False).head(n_recommendations).index
    similar_users_ratings = ratings_data.loc[most_similar_users]
    item_recommendations = similar_users_ratings.mean(axis=0).sort_values(ascending=False)
    already_rated = ratings_data.loc[user_id, ratings_data.loc[user_id] > 0].index
    recommendations = item_recommendations.drop(already_rated).head(n_recommendations)
    return recommendations.index

# Endpoint para la raíz de la API, proporcionando un mensaje de bienvenida y dirección a la documentación
@app.get("/")
async def root():
    return {"message": "Bienvenido a mi API FastAPI. Usa /docs para ver la documentación."}

# Los siguientes endpoints implementan la funcionalidad específica para cada conjunto de datos
# Cada uno procesa los datos pertinentes y devuelve información relevante basada en el parámetro de entrada

@app.get("/developer/{developer_name}")
async def developer(developer_name: str):
    df = dfs['df1']
    filtered_df = df[df['developer'].str.lower() == developer_name.lower()]
    grouped = filtered_df.groupby('release_anio').agg(total_items=('items_total', 'sum'), free_content_percentage=('items_free', lambda x: f"{(x.sum() / x.count() * 100):.2f}%")).reset_index()
    return {"developer": developer_name, "data": grouped.to_dict(orient='records')}

@app.get("/userdata/{user_id}")
async def userdata(user_id: str):
    df = dfs['df2']
    filtered_df = df[df['user_id'] == user_id]
    total_spent = filtered_df['cantidad total gastado'].sum()
    items_count = filtered_df['item_id'].nunique()
    percentage_of_recommendation = "0%" if filtered_df.empty else filtered_df.iloc[0]['percentage_true']
    return {"Usuario": user_id, "Dinero gastado": f"{total_spent} USD", "% de recomendación": percentage_of_recommendation, "Cantidad de items": items_count}

@app.get("/userforgebre/{genre}")
async def user_for_genre(genre: str):
    df = dfs['df3']
    filtered_df = df[df['genres'].str.contains(genre, case=False)]
    user_hours = filtered_df.groupby('user_id')['playtime_forever'].sum().reset_index()
    top_user = user_hours.loc[user_hours['playtime_forever'].idxmax()]
    hours_per_year = filtered_df.groupby('release_anio')['playtime_forever'].sum().reset_index()
    return {"Usuario con más horas jugadas para Género": genre, "user_id": top_user['user_id'], "Horas jugadas": hours_per_year.to_dict(orient='records')}

@app.get("/best_developer_year/{year}")
async def best_developer_year(year: int):
    df = dfs['df4']
    filtered_df = df[df['release_anio'] == year]
    positive_reviews_df = filtered_df[filtered_df['sentiment_analysis'] == 2]
    developers_ranking = positive_reviews_df.groupby('developer').size().reset_index(name='positive_reviews_count').sort_values(by='positive_reviews_count', ascending=False).head(3)
    return {"Año": year, "Top 3 desarrolladores": developers_ranking.to_dict(orient='records')}

@app.get("/developer_reviews_analysis/{developer_name}")
async def developer_reviews_analysis(developer_name: str):
    df = dfs['df5']
    filtered_df = df[df['developer'].str.lower() == developer_name.lower()]
    sentiment_counts = filtered_df['sentiment_analysis'].value_counts().to_dict()
    return {developer_name: {'Negative': sentiment_counts.get(0, 0), 'Positive': sentiment_counts.get(2, 0)}}

# Endpoint para recomendar ítems basados en la similitud con un ítem dado
@app.get("/recommend_items/{item_name}")
async def api_recommend_items(item_name: str, n_items: int = 5):
    recommended_items = recommend_items(item_name, n_items=n_items)
    return {"item_name": item_name, "recommended_items": list(recommended_items)}

# Endpoint para recomendar ítems a un usuario basado en la similitud con otros usuarios
@app.get("/recommendations_for_user/{user_id}")
async def get_recommendations_for_user(user_id: str, n_recommendations: int = 5):
    recommendations = recommend_items_for_user(user_id, n_recommendations=n_recommendations)
    return {"user_id": user_id, "recommendations": list(recommendations)}
