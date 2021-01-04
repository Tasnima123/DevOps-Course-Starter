from flask import Flask, redirect, url_for, render_template, request
import requests
import os
import datetime
from todo_app.flask_config import Config

def create_app(): 
    app = Flask(__name__)
    app.config.from_object(Config)

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

    API_KEY = os.environ.get("api_key")
    TOKEN = os.environ.get("token")

    _DEFAULT_ITEMS = []
    itemDict = []
    done_status = "5fa74971675c2824130b06db"
    doing_status = "5fa74971675c2824130b06da"
    toDo_status = "5fa74971675c2824130b06d9"

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
            "https://api.trello.com/1/boards/5fa74971675c2824130b06d8/cards?key="+API_KEY+"&token="+TOKEN)
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

if __name__ == '__main__':
    create_app().run()
