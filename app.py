from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import requests
import os
import pytz
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
client = MongoClient(os.getenv('MONGO_CLIENT_LINK'))
db = client[os.getenv('DB_NAME')]

class UserInput:
    def __init__(self, api_id, api_hash, bot_token, owner_id, timestamp, bot_name):
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.owner_id = owner_id
        self.timestamp = timestamp
        self.bot_name = bot_name

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        api_id = request.form['api_id']
        api_hash = request.form['api_hash']
        bot_token = request.form['bot_token']
        owner_id = request.form['owner_id']

        bot_info_response = requests.get(f'https://api.telegram.org/bot{bot_token}/getMe')
        bot_name = bot_info_response.json()['result']['username'] if bot_info_response.status_code == 200 else None

        local_tz = pytz.timezone('Asia/Kolkata')  
        timestamp = datetime.now(local_tz).strftime('%Y-%m-%d %I:%M:%S %p')

        user_input = UserInput(api_id=api_id, api_hash=api_hash, bot_token=bot_token, owner_id=owner_id, timestamp=timestamp, bot_name=bot_name)
        db.user_inputs.insert_one({
            'api_id': user_input.api_id,
            'api_hash': user_input.api_hash,
            'bot_token': user_input.bot_token,
            'owner_id': user_input.owner_id,
            'timestamp': user_input.timestamp,
            'bot_name': user_input.bot_name 
        })

        # Redirect to avoid form resubmission on page refresh
        return redirect(url_for('index'))

    inputs = db.user_inputs.find()
    return render_template('index.html', inputs=inputs)

@app.route('/show_database')
def show_database():
    inputs = db.user_inputs.find()
    return render_template('show_database.html', inputs=inputs)

@app.route('/delete_database', methods=['GET', 'POST'])
def delete_database():
    if request.method == 'GET':
        # Display a confirmation page before deleting
        return render_template('delete_confirm.html')

    elif request.method == 'POST':
        # Delete all entries in the user_inputs collection
        db.user_inputs.delete_many({})

        return redirect(url_for('index'))

@app.route('/delete_entry/<entry_id>', methods=['GET', 'POST'])
def delete_entry(entry_id):
    entry_id_obj = ObjectId(entry_id)
    db.user_inputs.delete_one({'_id': entry_id_obj})
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
