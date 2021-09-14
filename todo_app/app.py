from bson.objectid import ObjectId
from flask import Flask, redirect, url_for, render_template, request
from flask_login import LoginManager,login_required, login_user, current_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
from flask_session import Session
import os
import requests
import datetime
from bson.json_util import dumps
from bson.json_util import loads
from todo_app.flask_config import Config
from todo_app.classModels import Item, ViewModel, User
import pymongo

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
client = WebApplicationClient(client_id)

def create_app():
    app = Flask(__name__)
    sess = Session()
    app.secret_key = os.getenv("SECRET_KEY")
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    boolean_val = eval(os.getenv("disable_login"))
    app.config["LOGIN_DISABLED"]= boolean_val
    app.config.from_object(Config)
    username=os.getenv("MONGO_USER")
    password=os.getenv("MONGO_PASSWORD")
    url=os.getenv("MONGO_URL")
    database=os.getenv("MONGO_DB")
    protocol=os.getenv("MONGO_PROTOCOL")
    collection=os.getenv("MONGO_COLLECTION")
    MONGO_URI="{0}{1}:{2}@{3}/{4}?retryWrites=true&w=majority".format(protocol,username,password,url,database)
    mongo = pymongo.MongoClient(MONGO_URI)
    collections = mongo.MyDatabase.list_collection_names()
    if collection not in collections:
        todos = mongo.MyDatabase[collection]
    todos = mongo.MyDatabase[collection]
    _DEFAULT_ITEMS = []
    itemDict = []

    def check_role(func):
        def wrapper_function(*args, **kwargs):
            if 'writer' in current_user.roles:
                return func(*args, **kwargs)
        wrapper_function.__name__ = func.__name__
        return wrapper_function

    @app.route('/items', methods=["GET", "PATCH"])
    @app.route('/', methods=["GET", "PATCH"])
    @login_required
    def index():
        if (os.getenv("disable_login")=='True'):
            login_user(User("Testing"))
        items = get_cards()
        item_view_model = ViewModel(items)
        return render_template('index.html',view_model=item_view_model)

    @app.route('/items/<id>', methods=["GET", "POST"])
    @login_required
    def get(id):
        item = get_card(id)
        return render_template('saveItem.html', item = item)

    @app.route('/items/<id>/edit', methods=["GET", "POST", "PUT"])
    @login_required
    @check_role
    def edit(id):
        item = get_card(id)
        if request.method=="POST":
            item["title"]=request.form.get('itemTitle')
            item["status"]=request.form.get('itemStatus')
            save_card(item)
            return redirect(url_for('get', id = item["id"]))
        return render_template('edit.html', item = item)

    @app.route('/items/new', methods=["POST"])
    @login_required
    @check_role
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
        id_val = ObjectId()
        id_val = str(id_val)
        item = Item(id_val, title, 'To Do', date.date())
        itemDict.append(item)
        todos.insert_one({'_id': id_val, 'title': title,'status':'To Do','DateUpdated':date})
        return item

    def get_cards():
        data = list(todos.find())
        updated_data = loads(dumps(data))
        _DEFAULT_ITEMS = selectFields(updated_data)
        return _DEFAULT_ITEMS

    def selectFields(updated_data):
        for x in updated_data:
            id = x['_id']
            vals = [li['id'] for li in _DEFAULT_ITEMS]
            for value in vals:
                if value == id:
                    break
            else:
                title = x['title']
                status= x['status']
                date = x['DateUpdated']
                itemDict.append(Item(id, title, status, date))
                item = { 'id': id, 'title': title, 'status': status, 'DateUpdated': date }
                _DEFAULT_ITEMS.append(item)
        return _DEFAULT_ITEMS
    
    
    @app.route('/login/', methods=["GET", "POST"])
    def login():
        code = request.args.get('code')
        request_body = {
            "code":code,
            "client_id":client_id,
            "client_secret":client_secret
        }
        response = requests.post("https://github.com/login/oauth/access_token",request_body,headers={"Accept": "application/json"})
        parsed = client.parse_request_body_response(response.content)
        access_token = parsed["access_token"]
        github_user = requests.get("https://api.github.com/user",headers={"Authorization": "token {0}".format(access_token)}).json()
        user = load_user(github_user["login"])
        if login_user(user):
            return redirect("/")
        else:
            return "Error logging in."   
    
    @app.route('/logout', methods=['GET'])
    def logout():
        logout_user()
        return "Successfully logged out."

    login_manager = LoginManager()

    @login_manager.unauthorized_handler
    def unauthenticated():
        login_manager.login_view='auth.login'
        url = client.prepare_request_uri('https://github.com/login/oauth/authorize', redirect_uri='http://127.0.0.1:5000/login/')
        return redirect(url) 

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    login_manager.init_app(app)

    return app

if __name__ == '__main__':
    create_app.run()