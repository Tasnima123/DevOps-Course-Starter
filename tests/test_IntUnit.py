import pytest
from dotenv import load_dotenv, find_dotenv
from unittest.mock import patch
import os
from unittest.mock import Mock
from threading import Thread
from todo_app import app   
from todo_app.classModels import ViewModel

sample_trello_cards_response = [{"id": "5fb55f9084036928139db350", "name": "testTitle", "status": "To Do", "dateLastActivity": "2020-11-18T18:43:33.434Z"}]

@pytest.fixture
def client():
       file_path = find_dotenv('.env.test')
       load_dotenv(file_path, override=True)
       test_app = app.create_app()
       with test_app.test_client() as client:
          yield client

def test_viewModel():
       item = [{'id':"testID", 'title':"testTitle1", 'status':"To Do", 'DateUpdated':"testDate"},
       {'id': "testID", 'title': "testTitle2", 'status': "Doing", 'DateUpdated':"testDate"},
       {'id': "testID", 'title': "testTitle3", 'status': "Done", 'DateUpdated':"testDate"}]
       view_model = ViewModel(item)
       view_model.statusToDo
       view_model.statusDoing
       view_model.show_all_done_items
       assert len(view_model.statusToDo) == 1
       assert len(view_model.statusDoing) == 1
       assert len(view_model.show_all_done_items) == 1

def mock_get_cards(url):
       TRELLO_BOARD_ID = os.environ.get("TRELLO_BOARD_ID")
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

