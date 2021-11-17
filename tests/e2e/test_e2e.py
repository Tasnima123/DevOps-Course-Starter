import pytest
from selenium import webdriver
from threading import Thread
from todo_app import app
from dotenv import load_dotenv  
import time
import os
import pymongo
import logging

@pytest.fixture(scope='module')
def test_app():
    load_dotenv('.env', override=True)
    connection_string=os.getenv("MONGODB_CONNECTION_STRING")
    connection=pymongo.MongoClient(connection_string)
    new_collection = 'testCollection'
    os.environ["MONGO_COLLECTION"]=new_collection
    try:
        database = connection.get_database()
    except pymongo.errors.ConfigurationError:
        database = connection.get_database("project_exercise")
    logging.info('db name %s', database)
    os.environ["disable_login"]='True'
    application = app.create_app()
    thread = Thread(target=lambda: application.run(use_reloader=False))
    thread.daemon = True
    thread.start()
    yield app
    thread.join(1)
    database.testCollection.drop()

@pytest.fixture(scope="module")
def driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    with webdriver.Chrome('/usr/local/bin/chromedriver', options=opts) as driver:
        yield driver
    
def testDriver(test_app,driver):
    driver.get('http://127.0.0.1:5000/')
    assert driver.title == 'To-Do App'
    
def test_createTask(test_app,driver):
    testDriver(test_app,driver)
    time.sleep(3)
    driver.find_element_by_id("itemTitle").send_keys("Selenium_test")
    driver.find_element_by_id("submitButton").click()
    time.sleep(3)
    value = driver.find_element_by_id("toDo_list")
    time.sleep(2)
    assert "Selenium_test" in value.text

def test_moveDoing(test_app,driver):   
    testDriver(test_app,driver)
    time.sleep(3)
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
    time.sleep(3)
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



     