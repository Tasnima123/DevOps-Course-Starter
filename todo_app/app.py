from bson.objectid import ObjectId
from flask import Flask, redirect, url_for, render_template, request
from flask_login import LoginManager,login_required, login_user, current_user
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
from werkzeug.exceptions import Forbidden
import logging
from loggly.handlers import HTTPSHandler
from logging import Formatter

client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
redirect_uri_value = os.getenv("redirect_uri")
client = WebApplicationClient(client_id)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    sess = Session()
    app.secret_key = os.getenv("SECRET_KEY")
    app.logger.setLevel(app.config['LOG_LEVEL'])
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    if app.config['LOGGLY_TOKEN'] is not None:
        handler = HTTPSHandler(f'https://logs-01.loggly.com/inputs/{app.config["LOGGLY_TOKEN"]}/tag/todo-app')
        handler.setFormatter(Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))
        app.logger.addHandler(handler)
    collection=os.getenv("MONGO_COLLECTION")
    mongo_val = pymongo.MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
    try:
        db_name = mongo_val.get_database()
    except pymongo.errors.ConfigurationError:
        logging.warning('No default database. Using project_exercise database')
        db_name = mongo_val.get_database("project_exercise")
    app.logger.info('db name %s', db_name)
    collections = db_name.list_collection_names()
    if collection not in collections:
        todos = db_name[collection]
    todos = db_name[collection]
    _DEFAULT_ITEMS = []
    itemDict = []
    if os.getenv("disable_login")=='True':
        app.config["LOGIN_DISABLED"]=True

    def check_role(func):
        def wrapper_function(*args, **kwargs):
            if 'writer' in current_user.roles:
                return func(*args, **kwargs)
            else:
                app.logger.error('User does not have writer role enabled')
                raise Forbidden("Writer role required")
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
            app.logger.info("%s has been edited", request.form.get('itemTitle'))
            return redirect(url_for('get', id = item["id"]))
        return render_template('edit.html', item = item)

    @app.route('/items/new', methods=["POST"])
    @login_required
    @check_role
    def add():
        title = request.form.get('itemTitle')
        add_card(title)
        app.logger.info("%s has been added", request.form.get('itemTitle'))
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
            app.logger.info("User successfully logged in")
            return redirect("/")
        else:
            return app.logger.error("Error logging in")

    login_manager = LoginManager()

    @login_manager.unauthorized_handler
    def unauthenticated():
        login_manager.login_view='auth.login'
        url = client.prepare_request_uri('https://github.com/login/oauth/authorize', redirect_uri=redirect_uri_value)
        return redirect(url) 

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    login_manager.init_app(app)

    return app

if __name__ == '__main__':
    create_app.run()