from time import sleep
import pygetwindow as gw
from pyautogui import *
import pytesseract
from pymongo.mongo_client import MongoClient
from os import environ
from dotenv import load_dotenv
from google.oauth2 import service_account
import tkinter as tk
from PIL import ImageTk, Image

load_dotenv()

overlay = tk.Toplevel()
overlay.overrideredirect(True)
overlay.attributes("-topmost", True)

overlay_width = 250
overlay_height = 150
overlay.geometry(f"{overlay_width}x{overlay_height}")
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
        self.isGameRunning()
        self.notebookOpen = False
        if self.phasmophobia_running:
            self.img = ImageTk.PhotoImage(Image.open("guess.png"))
            self.label = tk.Label(overlay, image=self.img)
            print("Game's running ")
            self.checkIfFinished()
            self.checkIfNotebookOpen()
            sleep(0.8)

    def isGameRunning(self):
        try:
            phasmo = gw.getWindowsWithTitle("Phasmophobia")[0]
            if phasmo:
                self.phasmophobia_running = True
        except IndexError:
            print("Game is not launched")
            self.phasmophobia_running = False
            sleep(2)
            self.isGameRunning()
            

    def getGhostType(self, location):
        screenshot(
            "toRead.png", (location.left + location.width, location.top, 260, 80)
        )
        data = self.readSelectedGhostFromImage("toRead.png").strip()

        collection.update_one({"ghost": data}, {"$inc": {"count": 1}})
        selected_ghost = self.readSelectedGhostFromImage("guess.png").strip()
        match data:
            case "Raija":
                data = "Raiju"
            case "Deman":
                data = "Demon"
            case "Morai":
                data = "Moroi"
        match selected_ghost:
            case "Deman":
                selected_ghost = "Demon"
            case "Morai":
                selected_ghost = "Moroi"

        if selected_ghost == data:
            test_collection.update_one({"ghostType": data}, {"$inc": {"gamesPlayed": 1}})
            test_collection.update_one({"ghostType": data}, {"$inc": {"correctGuesses": 1}})
            print("Guessed")
        else:
            test_collection.update_one({"ghostType": data}, {"$inc": {"gamesPlayed": 1}})
            test_collection.update_one({"ghostType": data}, {"$inc": {"correctGuesses": 0}})
            print("Not guessed")
        print(data)
        print(selected_ghost)

    def checkIfNotebookOpen(self):
        if not self.notebookOpen:
            notebook = locateOnScreen("evidence.png", confidence=0.6)
            if notebook == None:
                print("Notebook closed")
            else:
                print("Notebook opened")
                try:
                    circle = locateOnScreen("circle.png", confidence=0.4)
                    print(circle)
                    screenshot(
                        "guess.png",
                        (
                            circle.left + (circle.width - (circle.width - 30)),
                            circle.top + (circle.height - (circle.height - 30)),
                            170,
                            37,
                        ),
                    )
                    sleep(2)
                except:
                    pass

    def readSelectedGhostFromImage(self, file):
        from google.cloud import vision

        client = vision.ImageAnnotatorClient(credentials=credentials)

        with open(file, "rb") as image_file:
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

                for i in range(300):
                    print(f"Cooldown: {i}")
                    sleep(1)

while True:
    Phasmophobia()