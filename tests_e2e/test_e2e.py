import pytest
from selenium import webdriver
from threading import Thread
from todo_app import app
from dotenv import load_dotenv, find_dotenv   
import time
import os
from todo_app import app
import requests

@pytest.fixture(scope='module')
def test_app():
       file_path = find_dotenv('.env')
       load_dotenv(file_path, override=True)
       board_id = create_trello_board()
       os.environ["TRELLO_BOARD_ID"] = board_id
       application = app.create_app()
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

def testDriver(test_app,driver):
    driver.get('http://127.0.0.1:5000/')
    assert driver.title == 'To-Do App'
    
def test_createTask(test_app,driver):
    testDriver(test_app,driver)
    driver.find_element_by_id("itemTitle").send_keys("Selenium_test")
    driver.find_element_by_id("submitButton").click()
    value = driver.find_element_by_id("toDo_list")
    time.sleep(2)
    assert "Selenium_test" in value.text

def test_moveDoing(test_app,driver):   
    testDriver(test_app,driver)
    driver.find_element_by_link_text('Selenium_test').click()
    driver.find_element_by_id("editButton").click()
    input = driver.find_element_by_id("itemStatus")
    input.clear()
    input.send_keys("Doing")
    driver.find_element_by_id("Update").click()
    driver.find_element_by_id("homepage").click()
    value = driver.find_element_by_id("Doing_list")
    time.sleep(2)
    assert "Selenium_test" in value.text

def test_moveDone(test_app,driver):
    testDriver(test_app,driver)
    driver.find_element_by_link_text('Selenium_test').click()
    driver.find_element_by_id("editButton").click()
    input = driver.find_element_by_id("itemStatus")
    input.clear()
    input.send_keys("Done")
    driver.find_element_by_id("Update").click()
    driver.find_element_by_id("homepage").click()
    value = driver.find_element_by_id("Done_list")
    time.sleep(2)
    assert "Selenium_test" in value.text

def create_trello_board():
    API_KEY = os.environ.get("api_key")
    TOKEN = os.environ.get("token")
    url = f"https://api.trello.com/1/boards/"
    query = {"key": API_KEY, "token": TOKEN, "name": 'TestBoard'}
    response = requests.request("POST",url,params=query)
    value = response.json()["id"]

    url = "https://api.trello.com/1/boards/"+value+"/lists"
    query = {"key": API_KEY, "token": TOKEN}
    response = requests.request("GET",url, params=query)
    os.environ["done_status"] = response.json()[0]["id"]
    os.environ["doing_status"] = response.json()[1]["id"]
    os.environ["toDo_status"] = response.json()[2]["id"]
    return value

def delete_trello_board(id):
    API_KEY = os.environ.get("api_key")
    TOKEN = os.environ.get("token")
    url = "https://api.trello.com/1/boards/"+id
    query = {
        'key': API_KEY,
        'token': TOKEN
        }
    requests.request("DELETE", url,params=query)




     