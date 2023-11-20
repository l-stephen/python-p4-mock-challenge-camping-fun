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
api = Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
   def get(self):
       campers = [camper.to_dict(rules=("-signups",)) for camper in Camper.query.all()]

       return campers, 200
   
   def post(self):
       fields = request.get_json()
       try:
           new_camper = Camper(
               name = fields["name"],
               age = fields["age"]
           )
           db.session.add(new_camper)
           db.session.commit()

           return new_camper.to_dict(), 201
       except ValueError:
           return {"errors": ["validation errors"]}, 400
   



class CampersByID(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()

        if camper is None:
            return {"error": "Camper not found"}, 404
        return camper.to_dict(rules=('signups',)), 200
    
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()

        if camper is None:
            return {"error": "Camper not found"}, 404
        
        fields = request.get_json()
        try:
            setattr(camper, 'name', fields['name'])
            setattr(camper, "age", fields['age'])
            db.session.add(camper)
            db.session.commit()

            return camper.to_dict(rules=('-signups',)), 202
        
        except ValueError:
            return {"errors": ["validation errors"]}, 400
    
class Activities(Resource):
    def get(self):
        act = [activity.to_dict() for activity in Activity.query.all()]
        return act, 200
    
class ActivitiesByID(Resource):
    def delete(self, id):
        act = Activity.query.filter_by(id=id).first()

        if act:
            db.session.delete(act)
            db.session.commit()
            return make_response({}, 204)
        return {"error": "Activity not found"}, 404
    
class Signups(Resource):
    def post(self):
        fields = request.get_json()
        try:
            signup = Signup(
                time = fields['time'],
                camper_id = fields['camper_id'],
                activity_id = fields['activity_id']
            )
            db.session.add(signup)
            db.session.commit()
            return signup.to_dict(rules=('activity',)), 201
        except ValueError:
            return {"errors": ["validation errors"]}, 400
        
api.add_resource(Campers, "/campers")
api.add_resource(CampersByID, "/campers/<int:id>")
api.add_resource(Activities, '/activities')
api.add_resource(ActivitiesByID, "/activities/<int:id>")
api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
