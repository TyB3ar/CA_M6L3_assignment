from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error 
from password import Password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{Password}@localhost/Fitness_Center_DB'
db = SQLAlchemy(app)
ma = Marshmallow(app) 


class MemberSchema(ma.Schema): # Schema for members 
    name = fields.String(required=True)
    age = fields.String(required=True)  
    
    class Meta:
        fields = ("name", "age", "id") 
        
member_schema = MemberSchema()  # can have one single member 
members_schema = MemberSchema(many=True)  # can have multiple members 


class SessionsSchema(ma.Schema): # Schema for WorkoutSessions
    session_date = fields.String(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True) 
    
    class Meta:
        fields = ("session_date", "session_time", "activity", "session_id", "member_id")
        
session_schema = SessionsSchema() 
sessions_schema = SessionsSchema(many=True)

class Members(db.Model):
    __tablename__ = "members"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.String(5))    



class Sessions(db.Model):
    __tablename__ = "sessions"
    session_id = db.Column(db.Integer, primary_key=True)   
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(25))
    activity = db.Column(db.String(50)) 
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    

# CRUD operations for Members: 
@app.route('/members', methods=['GET']) # DONE 
def get_members():
    members = Members.query.all()
    return members_schema.jsonify(members) 


@app.route('/members', methods=['POST']) # DONE
def add_member():
    try:
        member_data = member_schema.load(request.json) # validate and deserialize input
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Members(name=member_data['name'], age=member_data['age'])  # add new info into table
    db.session.add(new_member) # commit the add 
    db.session.commit()  # save and finalize the add 
    return jsonify({"message" : "New member added successfully."}), 201


@app.route('/members/<int:id>', methods=['PUT']) # DONE
def update_member(id):
    member = Members.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400 
    
    member.name = member_data['name']
    member.age = member_data['age'] 
    db.session.commit()
    return jsonify({"message" : "Member details updated successfully."}), 200


@app.route('/members/<int:id>', methods=['DELETE']) # DONE
def delete_member(id):
    member = Members.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"messasge" : "Member removed successfully."}), 200 



# CRUD operations for WorkoutSessions:
@app.route('/sessions', methods=['GET']) # DONE
def get_sessions():
    sessions = Sessions.query.all()
    return sessions_schema.jsonify(sessions) 


@app.route('/sessions', methods=['POST']) # DONE
def add_session():
    try: 
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_session = Sessions(session_date=session_data["session_date"], session_time=session_data["session_time"], activity=session_data["activity"], member_id=session_data['member_id']) 
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"message" : "New Session added successfully."}), 201


@app.route('/sessions/<int:session_id>', methods=['PUT']) # DONE
def update_session(session_id):
    session = Sessions.query.get_or_404(session_id)
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    session.session_date = session_data['session_date']
    session.session_time = session_data['session_time']
    session.activity = session_data['activity']
    session.member_id = session_data['member_id'] 
    db.session.commit()
    return jsonify({"message" : "Workout Session details updated successfully"}), 201  


@app.route('/sessions/<int:session_id>', methods=['DELETE']) # DONE
def delete_session(session_id):
    session = Sessions.query.get_or_404(session_id)
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message" : "Workout Session removed successfully."}), 200  


@app.route('/members/<int:member_id>/sessions', methods=["GET"]) # DONE 
def get_member_sessions(member_id):
    member = Members.query.get_or_404(member_id)
    sessions = Sessions.query.filter_by(member_id=member_id).all()
    return sessions_schema.jsonify(sessions)
      

if __name__ == '__main__':
    app.run(debug=True) 
