import pymongo
import pytest
from dotenv import load_dotenv
from unittest.mock import patch
import os
import mongomock
from todo_app import app   
from todo_app.classModels import ViewModel

sample_cards_response = {"_id": 3, "title": "testTitle", "status": "To Do", "DateUpdated": "2020-11-18T18:43:33.434Z"}

@pytest.fixture
def client():
       load_dotenv('.env.test', override=True)
       url = os.getenv("MONGO_URL")
       with mongomock.patch(servers=((url, 27017),)):
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

def mongo_setup():
       username = os.getenv("MONGO_USER")
       password = os.getenv("MONGO_PASSWORD")
       database = os.getenv("MONGO_DB")
       url = os.getenv("MONGO_URL")
       protocol = os.getenv("MONGO_PROTOCOL")
       db = pymongo.MongoClient(protocol+username+":"+password+"@"+url+"/"+database+"?retryWrites=true&w=majority")
       db.MyDatabase.todos.insert_one(sample_cards_response)

def test_index_page(client):
       mongo_setup()
       response = client.get('/')
       assert "testTitle" in response.data.decode() 

