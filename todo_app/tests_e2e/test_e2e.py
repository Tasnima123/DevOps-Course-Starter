import pytest
from selenium import webdriver
from todo_app.tests import test_Int

@pytest.fixture(scope="module")
def driver():
    with webdriver.Firefox() as driver:
        yield driver

@pytest.fixture(scope='module')
def test():
    with test_Int.test_app() as test_app:
        yield test_app

def test_task_journey(driver):
    driver.get('http://127.0.0.1:5000/')
    assert driver.title == 'To-Do App'



     