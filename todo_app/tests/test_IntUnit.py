import pytest
from dotenv import load_dotenv, find_dotenv
from unittest.mock import patch
import os
from unittest.mock import Mock
from threading import Thread
from todo_app import app   

sample_trello_cards_response = [{"id": "5fb55f9084036928139db350", "name": "testTitle", "status": "To Do", "dateLastActivity": "2020-11-18T18:43:33.434Z"}]

@pytest.fixture(scope='module')
def test_app():
       file_path = find_dotenv('.env.test')
       load_dotenv(file_path, override=True)
       application = app.create_app()
       thread = Thread(target=lambda: application.run(use_reloader=False))
       thread.daemon = True
       thread.start()
       yield app 
       thread.join(1)

@pytest.fixture
def client():
       file_path = find_dotenv('.env.test')
       load_dotenv(file_path, override=True)
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

def mock_get_cards(url):
       TRELLO_BOARD_ID = os.environ.get("TRELLO_BOARD_ID")
       # url = "https://api.trello.com/1/boards/"+TRELLO_BOARD_ID+"/cards"
       API_KEY = os.environ.get("api_key")
       TOKEN = os.environ.get("token")
       if url == f"https://api.trello.com/1/boards/"+TRELLO_BOARD_ID+"/cards?key="+API_KEY+"&token="+TOKEN:
              print("URL was hit")
              response = Mock()
              response.status_code = 200
              response.json.return_value = sample_trello_cards_response 
              return response
       return None

@patch('requests.get')
def test_index_page(mock_get_requests, client):
       mock_get_requests.side_effect = mock_get_cards
       response = client.get('/')
       assert "testTitle" in response.data.decode() 
