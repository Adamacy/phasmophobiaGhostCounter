from dotenv import load_dotenv
load_dotenv()
from os import environ
from pymongo.mongo_client import MongoClient
from fastapi import FastAPI
app = FastAPI()
from bson.json_util import dumps

MONGO_USERNAME = environ.get("MONGO_USERNAME")
MONGO_PASSWORD = environ.get("MONGO_PASSWORD")

MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.g0scwhz.mongodb.net/?retryWrites=true&w=majority"

ghosts = ['Banshee', 'Demon', 'Deogen', 'Goryo', 'Hantu', 'Jinn', 'Mare', 'Moroi', 'Myling', 'Obake', 'Oni', 'Onryo', 'Phantom', 'Poltergeist', 'Raiju', 'Revenant', 'Shade', 'Spirit', 'Thaye', 'The Mimic', 'The Twins', 'Wraith', 'Yokai', 'Yurei']
client = MongoClient(MONGO_URI)
db = client.phasmophobia
collection = db.ghosts

@app.get("/")
def index():
    return {"Message": "Welcome to: Phasmophobia Ghost Counter. Use /redoc to check avaiable endpoints"}

@app.get("/inc/{ghost}")
async def inc_ghost(ghost):
    if ghost in ghosts:
        collection.update_one({"ghost": ghost}, {"$inc": {"count": 1}})
        data = dumps(collection.find())
        return data
    else:
        return {"message": f"Wrong Ghost: {ghost}"}

@app.get("/dec/{ghost}")
def dec_ghost(ghost: str):
    if ghost in ghosts: 
        collection.update_one({"ghost": ghost}, {"$inc": {"count": -1}})
        data = dumps(collection.find())
        
        return data
    else:
        return {"message": f"Wrong Ghost: {ghost}"}