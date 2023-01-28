import os
from flask import Flask, render_template, url_for, request, redirect
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)

client = MongoClient(os.environ.get('MONGODB_URI'))
db=client[os.environ.get('DATABASE_NAME')]
collection_name=os.environ.get('COLLECTION_NAME')


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method=="POST":
        todo_title = request.form.get('todo_title')
        todo_desc = request.form.get('todo_desc')
        db[collection_name].insert_one({'title':todo_title, 'desc': todo_desc, 'status':'incomplete'})
    return render_template('bootstrap_index.html', todos=[entry for entry in db[collection_name].find({})])


@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    obj_id=ObjectId(id)
    db[collection_name].delete_one({'_id':obj_id})
    return redirect(url_for('home'))


# @app.route('/update/<id>', methods=['GET', 'POST'])
# def update(id):
#     if request.method=='POST':
#         todo_title = request.form.get('todo_title')
#         todo_desc = request.form.get('todo_desc')
#         db.Todo.insert_one({'title':todo_title, 'desc': todo_desc})
#         return redirect(url_for('home'))
#     update_todo = db.Todo.find_one({'_id':ObjectId(id)})
#     db.Todo.delete_one({'_id':ObjectId(id)})
#     print(update_todo)
#     return render_template('bootstrap_update.html', old_todo=update_todo)

@app.route('/complete/<id>', methods=['GET','POST'])
def complete(id): 
    obj_id = ObjectId(id)
    todo = db[collection_name].find_one({'_id':obj_id})
    filter={"_id":obj_id}
    if todo['status']=='Complete':
        update={"$set":{"status":"InComplete"}}
        db[collection_name].update_one(filter, update)
    else:
        update={"$set":{"status":"Complete"}}
        db[collection_name].update_one(filter, update)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)