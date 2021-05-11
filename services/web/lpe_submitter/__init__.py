import string
import random
import datetime
import uuid
import sqlalchemy
import logging
import logging.handlers
import json
import time
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

from flask import Flask, session, redirect, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('lpe_submitter.config.Config')
db = SQLAlchemy(app)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(36))
    exe = db.Column(db.LargeBinary)
    status = db.Column(db.String(36))
    output = db.Column(db.String)
    name = db.Column(db.String)

@app.route('/submit', methods=['POST'])
def submit():
    file = request.files['file'].read()
    name = request.form['name']
    submission = Submission(
        uuid=str(uuid.uuid4()),
        exe=file,
        status="NEW",
        output="",
        name=name
    )
    db.session.add(submission)
    db.session.commit()
    return """id: %s, uuid: %s, <a href="/check?uuid=%s">check link</a>""" % (submission.id, submission.uuid,submission.uuid)

@app.route('/check', methods=['GET'])
def check():
    _uuid = request.args.get('uuid', '')
    submission = db.session.query(Submission).filter(Submission.uuid==_uuid).first()
    if not submission:
        return "No such submission", 404
    else:
        output = submission.output
        if output.startswith('\\x'):
            output = bytes.fromhex(output[2:]).decode('utf-8')
        return """<pre>ID: %s
UUID: %s
name: %s
status: %s
output
-----------------------------
%s</pre>""" %( submission.id,submission.uuid,submission.name,submission.status,output)

@app.route('/stats')
def stats():
    subs = []
    for sub in db.session.query(Submission).order_by(Submission.id.asc()).all():
        subs.append({
            'id' : sub.id,
            'status' : sub.status,
            'name' : sub.name,
        })
    return json.dumps(subs, indent=4)
