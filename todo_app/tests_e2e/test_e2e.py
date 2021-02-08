import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from threading import Thread
from todo_app import app
from dotenv import load_dotenv, find_dotenv   
import os
from todo_app import app

@pytest.fixture(scope='module')
def test_app():
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
        driver.close()

def test_task_journey(test_app,driver):
    driver.get('http://127.0.0.1:5000/')
    assert driver.title == 'To-Do App'
    driver.find_element_by_id("itemTitle").send_keys("Selenium_test")
    driver.find_element_by_id("submitButton").click()
    value = driver.find_element_by_id("toDo_list")
    assert "Selenium_test" in value.text

def test_moveDoing(test_app,driver):   
    driver.find_element_by_link_text('Selenium_test').click()
    driver.find_element_by_id("editButton").click()
    input = driver.find_element_by_id("itemStatus")
    input.clear()
    input.send_keys("Doing")
    driver.find_element_by_id("Update").click()
    driver.find_element_by_id("homepage").click()
    value = driver.find_element_by_id("Doing_list")
    assert "Selenium_test" in value.text

def test_moveDone(test_app,driver):
    driver.find_element_by_link_text('Selenium_test').click()
    driver.find_element_by_id("editButton").click()
    input = driver.find_element_by_id("itemStatus")
    input.clear()
    input.send_keys("Done")
    driver.find_element_by_id("Update").click()
    driver.find_element_by_id("homepage").click()
    value = driver.find_element_by_id("Done_list")
    assert "Selenium_test" in value.text





     