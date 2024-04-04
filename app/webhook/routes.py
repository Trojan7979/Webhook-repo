from flask import Blueprint, jsonify, render_template, request
from datetime import datetime


from ..extensions import database
from flask import render_template
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')




# Receiver end point
@webhook.route('/', methods=["POST"])
def recipient():
    print("Received a webhook request.")
    if request.headers['Content-Type'] == 'application/json':
        payload = request.json
        action = payload.get('action')
        author = payload.get('pull_request', {}).get('user', {}).get('login')
        if "pusher" in payload:
            ref = payload.get('ref')
            to_branch = ref.split('/')[-1]  # Extracting branch name from ref
            pushed_by = payload.get('pusher', {}).get('name')
            times = payload.get('head_commit', {}).get('timestamp')
            database.insert_one({
                'request_id':None,
                'author':pushed_by,
                'action':'push',
                'from_branch':None,
                'to_branch':to_branch,
                'timestamp':times
            })
        elif action == 'closed' and payload.get('pull_request', {}).get('merged'):
            merged_id = payload.get('pull_request', {}).get('id')
            to_branch = payload.get('pull_request', {}).get('base', {}).get('ref')
            base_branch = payload.get('pull_request', {}).get('head', {}).get('ref')
            times = payload.get('pull_request', {}).get('updated_at')
            database.insert_one({
                'request_id':merged_id,
                'author':author,
                'action':action,
                'from_branch':head_branch,  
                'to_branch':base_branch,
                'timestamp':times
            }) 
        elif action == 'opened':
            pull_id = payload.get('pull_request', {}).get('id')
            base_branch = payload.get('pull_request', {}).get('base', {}).get('ref')
            head_branch = payload.get('pull_request', {}).get('head', {}).get('ref')
            timestamp = payload.get('pull_request', {}).get('created_at')
            database.insert_one({
                'request_id':pull_id,
                'author':author,
                'action':action,
                'from_branch':head_branch,
                'timestamp':timestamp
            })
    return {}, 200

#The UI will keep pulling data from MongoDB every 15 seconds and display the latest changes
@webhook.route('/ui', methods=["GET"])
def api_route():
    pull_requests_data = collection.find()
    return render_template('index.html', pull_requests=pull_requests_data)


@webhook.route('/api')
def get_data():
    pull_requests = collection.find()
    #ObjectId to strings
    pull_requests = [{**pr, '_id': str(pr['_id'])} for pr in pull_requests]
    return jsonify(pull_requests)



from ..extensions import collection
from flask import render_template
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')