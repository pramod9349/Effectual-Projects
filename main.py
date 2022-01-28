from fastapi import FastAPI
from scrape import scrape

app = FastAPI()

@app.get('/fetch/{id}')
def index(id):
    print(id)
    return scrape(id)