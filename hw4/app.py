from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
import config
from bson.objectid import ObjectId
app = Flask(__name__)
app.secret_key = 'your_secret_key'

client = MongoClient(config.MONGO_URI)
db = client['mydatabase']

# Ensure admin user exists
db.users.update_one(
    {"username": "admin"},
    {"$set": {"password": "admin"}},
    upsert=True
)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = db.users.find_one({"username": username, "password": password})

    if user:
        session['user'] = username
        return jsonify(success=True)
    return jsonify(success=False, message="Invalid credentials")

@app.route('/homepage')
def homepage():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    return render_template('homepage.html')


@app.route('/create')
def create_entry_page():
    return render_template('create_entry.html')

@app.route('/entries', methods=['GET'])
def get_entries():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    entries = db.entries.find()
    entry_list = [{"id": str(entry['_id']), "title": entry['title'], "content": entry['content']} for entry in entries]
    return jsonify(entries=entry_list)


@app.route('/create', methods=['POST'])
def create_entry():
    title = request.form['title']
    content = request.form['content']

    db.entries.insert_one({"title": title, "content": content})
    return jsonify(success=True)

@app.route('/entries/<entry_id>', methods=['PUT'])
def update_entry(entry_id):
    if 'user' not in session:
        return jsonify(success=False, message="Unauthorized"), 401

    title = request.json.get('title')
    content = request.json.get('content')

    if not title or not content:
        return jsonify(success=False, message="Title and content are required"), 400

    result = db.entries.update_one({'_id': ObjectId(entry_id)}, {"$set": {"title": title, "content": content}})

    if result.matched_count == 0:
        return jsonify(success=False, message="Entry not found"), 404

    return jsonify(success=True)

@app.route('/entries/<entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    if 'user' not in session:
        return jsonify(success=False, message="Unauthorized"), 401

    result = db.entries.delete_one({'_id': ObjectId(entry_id)})


    return jsonify(success=True)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
