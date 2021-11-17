import pymongo
import pytest
from dotenv import load_dotenv
import os
import mongomock
from todo_app import app   
from todo_app.classModels import ViewModel

sample_cards_response = {"id": 1, "title": "testTitle", "status": "To Do", "DateUpdated": "2020-11-18T18:43:33.434Z"}

@pytest.fixture
def client():
       load_dotenv('.env.test', override=True)
       os.environ["disable_login"]='True'
       with mongomock.patch(servers=(("test.mongo.cosmos.azure.com",10255),)):
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
       collection=os.getenv("MONGO_COLLECTION")
       mongo_val = pymongo.MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
       try:
        db_name = mongo_val.get_database()
       except pymongo.errors.ConfigurationError:
              db_name = mongo_val.get_database("project_exercise")
       collections = db_name.list_collection_names()
       if collection not in collections:
              todos = db_name[collection]
       todos = db_name[collection]
       todos.insert_one(sample_cards_response)

def test_index_page(client):
       mongo_setup()
       response = client.get('/')
       assert "testTitle" in response.data.decode() 

