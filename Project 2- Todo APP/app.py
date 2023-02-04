## Authentication is done,
    ## 1. Deploy Todo APP on cloud

import os, functools
from flask import Flask, render_template, url_for, request, redirect, session, flash
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

client = MongoClient(os.environ.get('MONGODB_URI'))
db=client[os.environ.get('DATABASE_NAME')]
collection_name=os.environ.get('COLLECTION_NAME')


def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for("login"))
        return route(*args, **kwargs)
    return route_wrapper

@app.route('/clear_session')
def clear_session():
    session.clear()
    return redirect(url_for('login'))

def credentials_present(email, password, all_docs):
    for doc in all_docs:
        if doc['email']==email and doc['password']==password:
            return True
    return False

def user_alreay_exist(email):
    all_docs = db[collection_name].find()
    for doc in all_docs:
        if doc['email']==email:
            return True
    return False

def getting_old_todos(email):
    all_docs = db[collection_name].find({'email':email})
    for doc in all_docs:
        return doc['todos']

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method=="POST":
        login_email = request.form.get('login_email')
        login_pass = request.form.get('login_password')
        ## check in database to match with email and pass
        ## provide proper checking login_email and login_pass

        login_email=login_email.strip()
        login_pass=login_pass.strip()

        if len(login_email)==0 or len(login_pass)==0:
            flash('Please Fill proper details')
        else:
            ## Now, getting email and password from mongodb
            all_documents = db[collection_name].find()
            if credentials_present(login_email,login_pass,all_documents):
                session["email"]=login_email
                return redirect(url_for('home'))
            else:
                flash('Sorry, Email or password is wrong!!')
    return render_template('bootstrap_login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        signup_email = request.form.get('signup_email').strip()
        signup_pass = request.form.get('signup_password').strip()
        signup_confirm_pass = request.form.get('signup_confirm_password').strip()

        if len(signup_email)==0 or len(signup_pass)==0 or len(signup_confirm_pass)==0:
            flash('Please provide proper details!!')
        else:
            ## Now, we are going to check password and confirm password
            ## and then, insert entry into database
            if signup_pass == signup_confirm_pass:
                if user_alreay_exist(signup_email)==False:
                    session['email']=signup_email
                    db[collection_name].insert_one({'email':signup_email, 'password': signup_pass, 'todos': []})
                    return redirect(url_for('login'))
                else:
                    flash('User already exist!!')
            else:
                flash('Password and Confirm Password does not match!!')
    return render_template('bootstrap_signup.html')


@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    user_email = session['email']
    if request.method=="POST":
        todo_title = request.form.get('todo_title')
        todo_desc = request.form.get('todo_desc')
        filter={"email":user_email}
        old_todos = getting_old_todos(user_email)
        new_todo = {
            'title':todo_title,
            'description': todo_desc,
            'status':'InComplete'
        }
        old_todos.append(new_todo)
        update = {"$set":{"todos":old_todos}}
        db[collection_name].update_one(filter, update)
    return render_template('bootstrap_index.html', todos=getting_old_todos(user_email), user_email = user_email)


@app.route('/delete/<email>/<title>/<desc>', methods=['GET', 'POST'])
@login_required
def delete(email, title, desc):
    old_todos = getting_old_todos(email)
    new_todos=[]
    for todo in old_todos:
        if not (todo['title']==title and todo['description']==desc):
            new_todos.append(todo)
    filter = {"email": email}
    update = {"$set": {"todos":new_todos}}
    db[collection_name].update_one(filter, update)
    return redirect(url_for('home'))


@app.route('/Complete/<email>/<title>/<desc>', methods=['GET', 'POST'])
@login_required
def complete(email, title, desc):
    old_todos = getting_old_todos(email)
    new_todos=[]
    for todo in old_todos:
        if todo['title']==title and todo['description']==desc:
            new_todo={
                'title':title,
                'description': desc,
                'status': 'Complete'
            }
            new_todos.append(new_todo)
        else:
            new_todos.append(todo)
        filter={'email': email}
        update = {'$set':{'todos':new_todos}}
        db[collection_name].update_one(filter, update)
    return redirect(url_for('home'))


@app.route('/InComplete/<email>/<title>/<desc>', methods=['GET', 'POST'])
@login_required
def incomplete(email, title, desc):
    old_todos = getting_old_todos(email)
    new_todos=[]
    for todo in old_todos:
        if todo['title']==title and todo['description']==desc:
            new_todo={
                'title':title,
                'description': desc,
                'status': 'InComplete'
            }
            new_todos.append(new_todo)
        else:
            new_todos.append(todo)
        filter={'email': email}
        update = {'$set':{'todos':new_todos}}
        db[collection_name].update_one(filter, update)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)