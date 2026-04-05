from fastapi import FastAPI
from fastapi.responses import HTMLResponse 


app = FastAPI()

movies = {
    "id": 1, "title": "The Shawshank Redemption", "year": 1994,
    "id": 2, "title": "The Godfather", "year": 1972,
    "id": 3, "title": "The Dark Knight", "year": 2008,
    "id": 4, "title": "Pulp Fiction", "year": 1994,
     }
app.title = "Mi primer APP con FastAPI"


@app.get("/", tags=["Home"])
def home():
    return "Hola Mundo"



@app.get("/movies", tags=["Home"])
def get_movies():
    return movies