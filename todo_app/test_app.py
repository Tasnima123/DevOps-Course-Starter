import pytest
from dotenv import load_dotenv, find_dotenv
from unittest.mock import patch
import requests
import os
from todo_app import app

id = ""

def create_board():
       url = "https://api.trello.com/1/boards/"
       query = {
          'key': os.environ.get("api_key"),
          'token': os.environ.get("token"),
          'name': 'TestCase'
         }
       response = requests.request("POST",url,params=query)
       id = response.json()["id"]

def delete_board():
      url = "https://api.trello.com/1/boards/"+id
      query = {
      'key': os.environ.get("api_key"),
      'token': os.environ.get("token")
      }
      response = requests.request("DELETE", url,params=query)

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

                   

