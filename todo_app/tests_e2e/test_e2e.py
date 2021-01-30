import pytest
from selenium import webdriver
from todo_app.tests.test_IntUnit import test_app
from threading import Thread
from todo_app import app
from dotenv import load_dotenv, find_dotenv   
import os
import requests

API_KEY = os.environ.get("api_key")
TOKEN = os.environ.get("token")

def create_trello_board():
    url = f"https://api.trello.com/1/boards/"
    query = {"key": API_KEY, "token": TOKEN, "name": 'TestCase'}
    response = requests.request("POST",url,params=query)
    value = response.json()["id"]
    return value

def delete_trello_board(id):
    url = "https://api.trello.com/1/boards/"+id
    query = {
      'key': API_KEY,
      'token': TOKEN
      }
    requests.request("DELETE", url,params=query)

@pytest.fixture(scope='module')
def app_with_temp_board():
       board_id = create_trello_board()
       os.environ['TRELLO_BOARD_ID'] = board_id
       application = app.create_app()
       file_path = find_dotenv('.env.test')
       load_dotenv(file_path, override=True)
       thread = Thread(target=lambda: application.run(use_reloader=False))
       thread.daemon = True
       thread.start()
       yield app 
       thread.join(1)
       delete_trello_board(board_id)

@pytest.fixture(scope="module")
def driver():
    with webdriver.Firefox() as driver:
        yield driver

@pytest.mark.usefixtures("test_app")
def test_task_journey(driver, app_with_temp_board):
    driver.get('http://127.0.0.1:5000/')
    assert driver.title == 'To-Do App'
    




     