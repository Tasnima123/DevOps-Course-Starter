import pytest
from selenium import webdriver
from threading import Thread
from todo_app import app
from dotenv import load_dotenv, find_dotenv   
import os
import time
from todo_app import app

@pytest.fixture(scope='module')
def test_app():
       file_path = find_dotenv('.env')
       load_dotenv(file_path, override=True)
       board_id = app.create_trello_board()
       application = app.create_app(board_id)
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





     