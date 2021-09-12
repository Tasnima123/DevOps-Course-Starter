import pytest
from selenium import webdriver
from threading import Thread
from todo_app import app
from dotenv import load_dotenv, find_dotenv   
import time
import os
import requests
import pymongo

@pytest.fixture(scope='module')
def test_app():
       file_path = find_dotenv('.env')
       load_dotenv(file_path, override=True)
       db = create_collection()
       database = db.MyDatabase
       application = app.create_app()
       thread = Thread(target=lambda: application.run(use_reloader=False))
       thread.daemon = True
       thread.start()
       yield app
       thread.join(1)
       database.testCollection.drop()

@pytest.fixture(scope='module')
def driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    with webdriver.Chrome('./chromedriver', options=opts) as driver:
        yield driver

def testDriver(test_app,driver):
    driver.get('http://127.0.0.1:5000/')
    assert driver.title == 'To-Do App'
    
def test_createTask(test_app,driver):
    testDriver(test_app,driver)
    driver.find_element_by_id("itemTitle").send_keys("Selenium_test")
    driver.find_element_by_id("submitButton").click()
    time.sleep(3)
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
    time.sleep(3)
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
    time.sleep(3)
    value = driver.find_element_by_id("Done_list")
    time.sleep(2)
    assert "Selenium_test" in value.text

def create_collection():
    username = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    url = os.getenv("MONGO_URL")
    protocol = os.getenv("MONGO_PROTOCOL")
    database = os.getenv("MONGO_DB")
    MONGO_URI = str(protocol+username+":"+password+"@"+url+"/"+database+"?retryWrites=true&w=majority")
    db = pymongo.MongoClient(MONGO_URI)
    new_collection = 'testCollection'
    os.environ["MONGO_COLLECTION"]=new_collection
    return db



     