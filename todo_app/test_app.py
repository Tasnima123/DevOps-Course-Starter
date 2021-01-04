import pytest
from dotenv import load_dotenv, find_dotenv
from unittest.mock import patch, Mock
from todo_app import app

@pytest.fixture
def client():
       file_path = find_dotenv('.env.test')
       load_dotenv(file_path, override=True)
       test_app = app.create_app()
       with test_app.test_client() as client:
          yield client

def get_requests():
   mock_get_requests = [{"id": "5fb55f9084036928139db350", "title": "Testing", "status": "To Do", "dateLastActivity": "2020-11-18T18:43:33.434Z"}]
   return mock_get_requests

@patch('requests.get')
def test_index(client):
   response = client.get('/')
   value = get_requests()
   for record in value:
            title = record['title']
            if not title:
                   assert False
                   break

                   

