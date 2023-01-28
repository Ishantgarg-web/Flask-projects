import os
import datetime
from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.environ.get("MONGODB_URI"))
db = client['Microblog']


@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method=='POST':
        post_title=request.form.get('post_title')
        post_content = request.form.get('content')
        today_date = datetime.datetime.today().strftime('%y-%m-%d')
        db.entries.insert_one({'title':post_title,'content':post_content,'createdAt':today_date})
    return render_template('bootstrap_index.html', entries=[e for e in db.entries.find({})])


@app.route('/recent_post_delete_btn/<id>', methods=["GET"])
def delete_post(id):
    db.entries.delete_one({"_id":ObjectId(id)})
    return redirect(url_for('home_page'))


if __name__=='__main__':
    app.run(debug=True)