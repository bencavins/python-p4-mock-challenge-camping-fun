#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def all_campers():
    if request.method == 'GET':
        campers = Camper.query.all()
        return [c.to_dict(rules=['-signups']) for c in campers], 200
    elif request.method == 'POST':
        json_data = request.get_json()

        new_camper = Camper(
            name=json_data.get('name'),
            age=json_data.get('age')
        )

        db.session.add(new_camper)
        db.session.commit()

        return new_camper.to_dict(rules=['-signups']), 201

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()

    if camper is None:
        return {'error': 'camper not found'}, 404
    
    if request.method == 'GET':
        return camper.to_dict(), 200
    elif request.method == 'PATCH':
        json_data = request.get_json()

        for field in json_data:
            setattr(camper, field, json_data[field])

        db.session.add(camper)
        db.session.commit()

        return camper.to_dict(rules=['-signups']), 200
    
@app.route('/activities', methods=['GET'])
def all_activities():
    activities = Activity.query.all()
    return [a.to_dict(rules=['-signups']) for a in activities], 200

@app.route('/activities/<int:id>', methods=['DELETE'])
def activity_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if activity is None:
        return {'error': 'activity not found'}, 404
    
    db.session.delete(activity)
    db.session.commit()

    return {}, 204

@app.route('/signups', methods=['POST'])
def all_signups():
    json_data = request.get_json()

    new_signup = Signup(
        time=json_data.get('time'),
        camper_id=json_data.get('camper_id'),
        activity_id=json_data.get('activity_id')
    )

    db.session.add(new_signup)
    db.session.commit()

    return new_signup.to_dict(), 201
