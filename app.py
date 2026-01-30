from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.github_events
events_col = db.events

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def github_webhook():
    event = request.headers.get('X-GitHub-Event')
    payload = request.json

    data = {}

    if event == 'push':
        data = {
            'author': payload['pusher']['name'],
            'action': 'push',
            'from_branch': None,
            'to_branch': payload['ref'].split('/')[-1],
            'timestamp': payload['head_commit']['timestamp']
        }

    elif event == 'pull_request':
        pr = payload['pull_request']
        if payload['action'] == 'closed' and pr.get('merged'):
            data = {
                'author': pr['user']['login'],
                'action': 'merge',
                'from_branch': pr['head']['ref'],
                'to_branch': pr['base']['ref'],
                'timestamp': pr['merged_at']
            }
        else:
            data = {
                'author': pr['user']['login'],
                'action': 'pull_request',
                'from_branch': pr['head']['ref'],
                'to_branch': pr['base']['ref'],
                'timestamp': pr['created_at']
            }

    if data:
        events_col.insert_one(data)

    return jsonify({'status': 'success'})

@app.route('/events')
def get_events():
    try:
        events = list(events_col.find().sort('_id', -1).limit(10))
        for e in events:
            e['_id'] = str(e['_id'])
        return jsonify(events)
    except Exception:
        # If DB is unavailable, return an empty list instead of a 500
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
