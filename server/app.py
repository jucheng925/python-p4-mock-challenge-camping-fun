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

api = Api(app=app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        resp = [camper.to_dict(rules=('-signups', )) for camper in campers]
        return make_response(resp, 200)
    
    def post(self):
        try:
            form_data = request.get_json()
            name = form_data.get('name')
            age = form_data.get('age')
            new_camper = Camper(age=age, name=name)
            db.session.add(new_camper)
            db.session.commit()
            return make_response(new_camper.to_dict(rules=('-signups', )), 201)
        except ValueError:
            resp = {"errors": ["validation errors"]}
            return make_response(resp, 400)
               
api.add_resource(Campers, '/campers')

class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            return make_response(camper.to_dict(), 200)
        else:
            resp = {"error": "Camper not found"}
            return make_response(resp, 404)
        
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            try:
                form_data = request.get_json()
                for attr in form_data:
                    setattr(camper, attr, form_data.get(attr))
                db.session.add(camper)
                db.session.commit()
                return make_response(camper.to_dict(), 202)
            except ValueError:
                resp = {"errors": ["validation errors"]}
                return make_response(resp, 400)
            
        else:
            resp = {"error": "Camper not found"}
            return make_response(resp, 404)
        

api.add_resource(CamperById, '/campers/<int:id>')

class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        resp = [activity.to_dict(rules = ('-signups',)) for activity in activities]
        return make_response(resp, 200)

api.add_resource(Activities, '/activities')

class ActivityById(Resource):
    def get(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            return make_response(activity.to_dict(), 200)
        else:
            resp = {"error": "Activity not found"}
            return make_response(resp, 404)


    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if activity:
            for signup in activity.signups:
                db.session.delete(signup)
                db.session.commit()
            db.session.delete(activity)
            db.session.commit()
            return make_response({}, 204)
        else:
            resp = {"error": "Activity not found"}
            return make_response(resp, 404)

api.add_resource(ActivityById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        form_data = request.get_json()
        try:
            camper_id = form_data["camper_id"]
            activity_id = form_data["activity_id"]
            time = form_data["time"]
            new_signup = Signup(camper_id=camper_id, activity_id=activity_id, time=time)
            db.session.add(new_signup)
            db.session.commit()
            return make_response(new_signup.to_dict(), 201)

        except ValueError:
            resp = { "errors": ["validation errors"] }
            return make_response(resp, 400)

api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
