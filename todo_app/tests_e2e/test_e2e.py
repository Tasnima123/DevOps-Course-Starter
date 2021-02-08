import pytest
from selenium import webdriver
from todo_app.tests.test_IntUnit import test_app
from threading import Thread
from todo_app import app
from dotenv import load_dotenv, find_dotenv   
import os
import requests
from todo_app import app

@pytest.fixture(scope='module')
def app_with_temp_board():
       file_path = find_dotenv('.env')
       load_dotenv(file_path, override=True)
       board_id = os.environ['TRELLO_BOARD_ID']
       board_id = app.create_trello_board()
       application = app.create_app()
       thread = Thread(target=lambda: application.run(use_reloader=False))
       thread.daemon = True
       thread.start()
       yield app 
       thread.join(1)
       app.delete_trello_board(board_id)

@pytest.fixture(scope="module")
def driver():
    with webdriver.Firefox() as driver:
        yield driver

def test_task_journey(driver):
    driver.get('http://localhost:5000/')
    assert driver.title == 'To-Do App'




     