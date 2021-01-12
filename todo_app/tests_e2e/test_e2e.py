import pytest
from selenium import webdriver
from todo_app.tests.test_IntUnit import test_app

@pytest.fixture(scope="module")
def driver():
    with webdriver.Firefox() as driver:
        yield driver

@pytest.mark.usefixtures("test_app")
def test_task_journey(driver, test_app):
    driver.get('http://127.0.0.1:5000/')
    assert driver.title == 'To-Do App'
    




     