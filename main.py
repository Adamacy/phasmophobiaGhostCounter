from time import sleep
import pygetwindow as gw
from pyautogui import *
import pytesseract
from pymongo.mongo_client import MongoClient
from os import environ
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()

# GCloud config
credentials = service_account.Credentials.from_service_account_file("private-key.json")

# PyTesseract location
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract"

# MongoDB settings
MONGO_USERNAME = environ.get("MONGO_USERNAME")
MONGO_PASSWORD = environ.get("MONGO_PASSWORD")
MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@cluster0.g0scwhz.mongodb.net/?retryWrites=true&w=majority"


client = MongoClient(MONGO_URI)
db = client.phasmophobia
collection = db.ghosts
test_collection = db.test_ghosts


class Phasmophobia:
    def __init__(self) -> None:
        self.finished = False
        self.phasmophobia_running = False
        self.notebookOpen = False
        self.isGameRunning()

    def isGameRunning(self):
        try:
            phasmo = gw.getWindowsWithTitle("Phasmophobia")[0]
            if phasmo:
                self.phasmophobia_running = True
                print("Running")
                sleep(0.5)
                self.checkIfFinished()
                self.checkIfNotebookOpen()
                self.isGameRunning()

        except IndexError:
            print("Game is not launched")
            self.phasmophobia_running = False
            sleep(2)
            self.isGameRunning()

    def getGhostType(self, location):
        screenshot(
            "toRead.png", (location.left + location.width, location.top, 250, 80)
        )
        data = pytesseract.image_to_string("toRead.png").strip()

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
            case "Mace":
                data = "Mare"
            case "Morai":
                data = "Moroi"
            case "M ora:":
                data = "Moroi"

        collection.update_one({"ghost": data}, {"$inc": {"count": 1}})
        selected_ghost = self.readSelectedGhostFromImage()
        if selected_ghost == data:
            test_collection.update_one({"ghost": data}, {"$inc": {"gamesPlayed": 1}})
            test_collection.update_one({"ghost": data}, {"$inc": {"correctGuesses": 1}})
        else:
            test_collection.update_one({"ghost": data}, {"$inc": {"gamesPlayed": 1}})
            test_collection.update_one({"ghost": data}, {"$inc": {"correctGuesses": 0}})

        print(data)
        print(selected_ghost)

    def checkIfNotebookOpen(self):
        if not self.notebookOpen:
            notebook = locateOnScreen("evidence.png")
            if notebook == None:
                print("Notebook closed")
            else:
                print("Notebook opened")
                try:
                    circle = locateOnScreen("circle.png", confidence=0.4)
                    screenshot(
                        "guess.png",
                        (
                            circle.left + (circle.width - (circle.width - 30)),
                            circle.top + (circle.height - (circle.height - 30)),
                            120,
                            28,
                        ),
                    )
                except:
                    pass

    def readSelectedGhostFromImage(self):
        from google.cloud import vision

        client = vision.ImageAnnotatorClient(credentials=credentials)

        with open("guess.png", "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(
                    response.error.message
                )
            )
        return texts[0].description

    def getSelectedGhost(self, location):
        screenshot(
            "guess.png",
            (
                location.left + (location.width - (location.width - 30)),
                location.top + (location.height - (location.height - 30)),
                120,
                28,
            ),
        )

    def checkIfFinished(self):
        if not self.finished:
            ghostType = locateOnScreen("ghost_type.png", confidence=0.50)
            if ghostType == None:
                self.finished = False
                print("Game not finished")
            else:
                self.finished = True
                print("Game finished")
                self.getGhostType(ghostType)

                sleep(300)


Phasmophobia()
