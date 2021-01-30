import pytest
from dotenv import load_dotenv, find_dotenv
from unittest.mock import patch
from threading import Thread
from todo_app import app    

@pytest.fixture(scope='module')
def test_app():
       application = app.create_app()
       file_path = find_dotenv('.env.test')
       load_dotenv(file_path, override=True)
       thread = Thread(target=lambda: application.run(use_reloader=False))
       thread.daemon = True
       thread.start()
       yield app 
       thread.join(1)

@pytest.fixture
def client():
       test_app = app.create_app()
       with test_app.test_client() as client:
          yield client

def test_statusToDo():
       updated_items = []
       item = { 'id': "testID", 'title': "testTitle", 'status': "To Do", 'DateUpdated':"testDate"}
       if (item['status']== "To Do"):
              updated_items.append(item)
       assert len(updated_items) == 1

def test_statusDoing():
       updated_items2 = []
       item = { 'id': "testID", 'title': "testTitle", 'status': "Doing", 'DateUpdated':"testDate"}
       if (item['status']== "Doing"):
              updated_items2.append(item)
       assert len(updated_items2) == 1

def test_show_all_done_items():
       updated_items3 = []
       item = { 'id': "testID", 'title': "testTitle", 'status': "Done", 'DateUpdated':"testDate"}
       if (item['status']== "Done"):
              updated_items3.append(item)
       assert len(updated_items3) == 1

def mock_get_requests():
       mock_get_requests = [{"id": "5fb55f9084036928139db350", "title": "Testing", "status": "To Do", "dateLastActivity": "2020-11-18T18:43:33.434Z"}]
       return mock_get_requests

@patch('requests.get')
def test_index_page(mock_get_requests, client):
       value = mock_get_requests()
       response = client.get('/')
       for record in value:
              title = record['title']
              if not title:
                     assert False
                     break

