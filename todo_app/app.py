from flask import Flask, redirect, url_for, render_template, request
import requests
import os
from todo_app.flask_config import Config

app = Flask(__name__)
app.config.from_object(Config)

class Item:
    def __init__(self, id, title, status):
        self.id = id
        self.title = title
        self.status = status

API_KEY = os.environ.get("api_key")
TOKEN = os.environ.get("token")
_DEFAULT_ITEMS = []
done_status = "5fa74971675c2824130b06db"
doing_status = "5fa74971675c2824130b06da"
toDo_status = "5fa74971675c2824130b06d9"

@app.route('/items', methods=["GET"])
@app.route('/', methods=["GET"])
def index():
    items = get_cards()
    items = sorted(items, key=lambda x:(x.get("status")!='To Do' or x.get("status")!='Doing', items))
    return render_template('index.html', items = items)

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

    _DEFAULT_ITEMS = updated_items
    return item

def add_card(title):
    url = f"https://api.trello.com/1/cards"
    querystring = {"name": title, "idList": toDo_status, "key": API_KEY, "token": TOKEN}
    response = requests.request("POST", url, params=querystring)
    card_id = response.json()["id"]
    item = Item(card_id, title, 'To Do')
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
            if (record.get('idList')==done_status):
                status = "Done"
            elif (record.get('idList')==toDo_status):
                status = "To Do"
            else:
                status = "Doing"
            item = { 'id': id, 'title': title, 'status': status }
            _DEFAULT_ITEMS.append(item)
    return _DEFAULT_ITEMS

if __name__ == '__main__':
    app.run()
