from fastapi import FastAPI
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Carga de datos desde archivos parquet
file_paths = {
    'df1': './data/dataset_endpoint_1.parquet',
    'df2': 'data/dataset_endpoint_2.parquet',
    'df3': 'data/dataset_endpoint_3.parquet',
    'df4': 'data/dataset_endpoint_4.parquet',
    'df5': 'data/dataset_endpoint_5.parquet',
    'recomendacion': 'data/df_recomendacion.parquet'
}

dfs = {key: pd.read_parquet(path) for key, path in file_paths.items()}

# Crear matriz de valoraciones para el modelo de recomendación
ratings_matrix = dfs['recomendacion'].pivot_table(index='user_id', columns='item_name', values='rating').fillna(0)

# Calcular la similitud de coseno entre ítems
item_similarity = cosine_similarity(ratings_matrix.T)
item_similarity_df = pd.DataFrame(item_similarity, index=ratings_matrix.columns, columns=ratings_matrix.columns)

# Función para recomendar ítems similares
def recommend_items(item_name, similarity_data=item_similarity_df, n_items=5):
    similar_scores = similarity_data[item_name].sort_values(ascending=False)
    top_items = similar_scores[1:n_items+1].index
    return top_items

# Endpoints
@app.get("/")
async def root():
    return {"message": "Bienvenido a mi API FastAPI. Usa /docs para ver la documentación."}

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
    percentage_of_recommendation = filtered_df.iloc[0]['percentage_true'] if not filtered_df.empty else "0%"
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

@app.get("/recommend_items/{item_name}")
async def api_recommend_items(item_name: str, n_items: int = 5):
    recommended_items = recommend_items(item_name, item_similarity_df, n_items)
    return {"item_name": item_name, "recommended_items": list(recommended_items)}
