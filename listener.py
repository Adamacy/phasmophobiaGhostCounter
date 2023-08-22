from pyautogui import *
from time import sleep
import pytesseract
import pygetwindow as gw
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
load_dotenv()
from os import environ

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract"

MONGO_USERNAME = environ.get("MONGO_USERNAME")
MONGO_PASSWORD = environ.get("MONGO_PASSWORD")

MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.g0scwhz.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)

db = client.phasmophobia
collection = db.ghosts

def checkIfFinished():
    ghostType = locateOnScreen("ghost_type.png", confidence=0.50)

    while ghostType == None:
        ghostType = locateOnScreen("ghost_type.png", confidence=0.50)
        print("Check")
        sleep(10)

    else:
        screenshot(
            "toRead.png", (ghostType.left + ghostType.width, ghostType.top, 250, 80)
        )
        data = pytesseract.image_to_string("toRead.png").strip()
        print(data)
        match data:
            case "Weaith":
                data = "Wraith"
            case "Spicit":
                data = "Spirit"
            case "Tian":
                data = "Jinn"
            case "Tina":
                data = "Jinn"
            case "Demen":
                data = "Demon"
            case "Yarei":
                data = "Yurei"
            case "Hontu":
                data = "Hantu"
            case "Myting":
                data = "Myling"
            case "Rai ja":
                data = "Raiju"
            case "Oboke.":
                data = "Obake"
            case "Oncyo":
                data = "Onryo"
            case "Oboke":
                data = "Obake"
            case "The Minnie.":
                data = "The Mimic"
            case "The Minnie":
                data = "The Mimic"
            case "Morai":
                data = "Moroi"
        print(data)
        collection.update_one({"ghost": data}, {"$inc": {"count": 1}})
        
        sleep(300)


def isGameRunning():
    try:
        phasmo = gw.getWindowsWithTitle("Phasmophobia")[0]
    except:
        return False
    
    if phasmo:
        checkIfFinished()
    else:
        isGameRunning()

while True:
    print(isGameRunning())
    sleep(10)