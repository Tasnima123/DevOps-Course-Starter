from flask import Flask, redirect, url_for, render_template, request
import requests
import os
import datetime
from todo_app.flask_config import Config

def create_app(board_id): 
    app = Flask(__name__)
    app.config.from_object(Config)

    API_KEY = os.environ.get("api_key")
    TOKEN = os.environ.get("token")
    TRELLO_BOARD_ID = board_id

    class Item:
        def __init__(self, id, title, status, date):
            self.id = id
            self.title = title
            self.status = status
            self.date = date

    class ViewModel:
        def __init__(self, items):
            self._items = items
            self._ToDo = items
            self._Doing = items
            self._Done = items
            self._recentDone = items
            self._olderDone = items
        
        @property
        def items(self):
            return self._items

        @property
        def statusToDo(self):
            updated_items = []
            for val in self._items:
                if (val['status']== "To Do"):
                    item = { 'id': val["id"], 'title': val["title"], 'status': "To Do", 'DateUpdated':val["DateUpdated"] }
                    updated_items.append(item)
            self._ToDo = updated_items
            return self._ToDo
        
        @property
        def statusDoing(self):
            updated_items2 = []
            for val in self._items:
                if (val['status']== "Doing"):
                    item = { 'id': val["id"], 'title': val["title"], 'status': "Doing", 'DateUpdated':val["DateUpdated"] }
                    updated_items2.append(item)
            self._Doing = updated_items2
            return self._Doing 
        
        @property
        def show_all_done_items(self):
            updated_items3 = []
            for val in self._items:
                if (val['status']== "Done"):
                    item = { 'id': val["id"], 'title': val["title"], 'status': "Done", 'DateUpdated':val["DateUpdated"] }
                    updated_items3.append(item)
            self._Done = updated_items3
            
            if len(self._Done) < 5:
                return self._Done
            else:
                updated_items3 = []
                updated_items4 = []
                present = datetime.now()
                for val in self._items:
                    value = datetime.strptime(val['DateUpdated'], "%d/%m/%Y")
                    item = { 'id': val["id"], 'title': val["title"], 'status': "Done", 'DateUpdated':val["DateUpdated"] }
                    if (value.date() == present.date()):
                        updated_items3.append(item)
                    else:
                        updated_items4.append(item)
                        self._olderDone = updated_items4
                        self._recentDone = updated_items3
                return self._recentDone

        @property
        def recent_done_items(self): 
                return self._recentDone 
        
        @property
        def older_done_items(self): 
            return self._olderDone

    _DEFAULT_ITEMS = []
    itemDict = []
    done_status = os.environ.get("done_status")
    doing_status = os.environ.get("doing_status")
    toDo_status = os.environ.get("toDo_status")

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
        existing_items = get_cards()
        updated_items = [item if item['id'] == existing_item['id'] else existing_item for existing_item in existing_items]

        url = "https://api.trello.com/1/cards/"+item['id']
        headers = {"Accept": "application/json" }
        if (item['status'] == "Done"):
            idList=done_status
        elif (item['status'] == "Doing"):
            idList=doing_status
        else:
            idList= toDo_status
        querystring = {"key": API_KEY, "token": TOKEN, 'status': item['status'], "name": item['title'], "idList": idList}
        response = requests.request("PUT",url,headers=headers,params=querystring)
        return item

    def add_card(title):
        url = f"https://api.trello.com/1/cards"
        querystring = {"name": title, "idList": toDo_status, "key": API_KEY, "token": TOKEN}
        response = requests.request("POST", url, params=querystring)
        card_id = response.json()["id"]
        date = datetime.datetime.now()
        itemDict.append(Item(card_id, title, 'To Do', date.date()))
        item = Item(card_id, title, 'To Do', date.date())
        return item

    def get_cards():
        trello_api = requests.get(
            "https://api.trello.com/1/boards/"+TRELLO_BOARD_ID+"/cards?key="+API_KEY+"&token="+TOKEN)
        data = trello_api.json()
        _DEFAULT_ITEMS = selectFields(data)
        return _DEFAULT_ITEMS

    def selectFields(data):
        for record in data:
            title = record.get('name')
            vals = [li['title'] for li in _DEFAULT_ITEMS]
            for value in vals:
                if value == title:
                    break
            else:
                id = record.get('id')
                date = record.get('dateLastActivity')
                date_time_obj = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
                if (record.get('idList')==done_status):
                    status = "Done"
                elif (record.get('idList')==toDo_status):
                    status = "To Do"
                else:
                    status = "Doing"
                itemDict.append(Item(id, title, status, date_time_obj.date()))
                item = { 'id': id, 'title': title, 'status': status, 'DateUpdated': date_time_obj.date() }
                _DEFAULT_ITEMS.append(item)
        return _DEFAULT_ITEMS
    return app

def create_trello_board():
    API_KEY = os.environ.get("api_key")
    TOKEN = os.environ.get("token")
    url = f"https://api.trello.com/1/boards/"
    query = {"key": API_KEY, "token": TOKEN, "name": 'TestBoard'}
    response = requests.request("POST",url,params=query)
    value = response.json()["id"]

    url = "https://api.trello.com/1/boards/"+value+"/lists"
    query = {"key": API_KEY, "token": TOKEN}
    response = requests.request("GET",url, params=query)
    os.environ["done_status"] = response.json()[0]["id"]
    os.environ["doing_status"] = response.json()[1]["id"]
    os.environ["toDo_status"] = response.json()[2]["id"]
    return value

def delete_trello_board(id):
    API_KEY = os.environ.get("api_key")
    TOKEN = os.environ.get("token")
    url = "https://api.trello.com/1/boards/"+id
    query = {
        'key': API_KEY,
        'token': TOKEN
        }
    requests.request("DELETE", url,params=query)

if __name__ == '__main__':
    create_app().run()
