from flask import render_template, Flask, request, redirect, url_for
from todo_app.data.session_items import get_item, get_items, save_item, delete_item, add_item

from todo_app.flask_config import Config

app = Flask(__name__)

app.config.from_object(Config)

@app.route('/items', methods=["GET"])
@app.route('/', methods=["GET"])
def index():
    items = get_items()
    items = sorted(items, key=lambda x:(x.get("status")!='Not Started', items))
    return render_template('index.html', items = items)

@app.route('/items/<id>', methods=["GET", "POST"])
def get(id):
    item = get_item(id)
    return render_template('saveItem.html', item = item)

@app.route('/items/<id>/edit', methods=["GET", "POST"])
def edit(id):
    item = get_item(id)
    if request.method=="POST":
        item["title"]=request.form.get('itemTitle')
        item["status"]=request.form.get('itemStatus')
        save_item(item)
        return redirect(url_for('get', id = item["id"]))
    return render_template('edit.html', item = item)


@app.route('/items/new', methods=["POST"])
def add():
    title = request.form.get('itemTitle')
    add_item(title)
    return redirect(url_for('index'))

@app.route('/items/<id>/delete', methods=["GET"])
def delete(id):
    delete_item(id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
