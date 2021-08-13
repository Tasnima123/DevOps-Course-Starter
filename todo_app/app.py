from flask import Flask, redirect, url_for, render_template, request
import requests
import os
import datetime
from bson.json_util import dumps
from bson.json_util import loads
from todo_app.flask_config import Config
from todo_app.classModels import Item, ViewModel
import pymongo

def create_app(): 
    app = Flask(__name__)
    app.config.from_object(Config)
    username = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    url = os.getenv("MONGO_URL")
    database = os.getenv("MONGO_DB")
    protocol = os.getenv("MONGO_PROTOCOL")
    collection = os.getenv("MONGO_COLLECTION")
    MONGO_URI = "{0}{1}:{2}@{3}/{4}?retryWrites=true&w=majority".format(protocol,username,password,url,database)
    mongo = pymongo.MongoClient(MONGO_URI)
    collections = mongo.myDatabase.list_collection_names()
    if collection not in collections:
        todos = mongo.MyDatabase[collection]

    _DEFAULT_ITEMS = []
    itemDict = []

    @app.route('/items', methods=["GET", "PATCH"])
    @app.route('/', methods=["GET", "PATCH"])
    def index():
        items = get_cards()
        item_view_model = ViewModel(items)
        return render_template('index.html',view_model=item_view_model)

    @app.route('/items/<id>', methods=["GET", "POST"])
    def get(id):
        item = get_card(id)
        return render_template('saveItem.html', item = item)

    @app.route('/items/<id>/edit', methods=["GET", "POST", "PUT"])
    def edit(id):
        item = get_card(id)
        if request.method=="POST":
            item["title"]=request.form.get('itemTitle')
            item["status"]=request.form.get('itemStatus')
            save_card(item)
            return redirect(url_for('get', id = item["id"]))
        return render_template('edit.html', item = item)

    @app.route('/items/new', methods=["POST"])
    def add():
        title = request.form.get('itemTitle')
        add_card(title)
        return redirect(url_for('index'))

    def get_card(id):
        items = get_cards()
        return next((item for item in items if item['id'] == id), None)

    def save_card(item):
        date = datetime.datetime.now()
        existing_items = get_cards()
        updated_items = [item if item['id'] == existing_item['id'] else existing_item for existing_item in existing_items]
        todos.update_one({"_id":item['id']},{"$set":{"title":item['title'],"status":item['status'],'DateUpdated':date}})
        return item

    def add_card(title):
        date = datetime.datetime.now()
        print (date)
        id_val = str(len(_DEFAULT_ITEMS))
        item = Item(id_val, title, 'To Do', date.date())
        itemDict.append(item)
        todos.insert_one({'_id': id_val, 'title': title,'status':'To Do','DateUpdated':date})
        return item

    def get_cards():
        data = list(todos.find())
        parsed = loads(dumps(data))
        _DEFAULT_ITEMS = selectFields(parsed)
        return _DEFAULT_ITEMS

    def selectFields(parsed):
        for x in parsed:
            title = x['title']
            vals = [li['title'] for li in _DEFAULT_ITEMS]
            for value in vals:
                if value == title:
                    break
            else:
                id = x['_id']
                status= x['status']
                date = x['DateUpdated']
                itemDict.append(Item(id, title, status, date))
                item = { 'id': id, 'title': title, 'status': status, 'DateUpdated': date }
                _DEFAULT_ITEMS.append(item)
        return _DEFAULT_ITEMS

    return app

if __name__ == '__main__':
    create_app().run()
