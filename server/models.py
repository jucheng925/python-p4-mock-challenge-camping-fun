from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship("Signup", back_populates="activity")
    campers = association_proxy('signups', 'camper', 
                    creator = lambda camper_obj: Signup(camper=camper_obj))
    
    # Add serialization rules
    serialize_rules =('-signups.activity', )
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # Add relationship

    signups = db.relationship("Signup", back_populates ='camper')
    activities = association_proxy('signups', 'activity', 
                        creator = lambda activity_obj : Signup(activity = activity_obj))
    
    # Add serialization rules

    serialize_rules = ('-signups.camper',)
    
    # Add validation
    @validates('name')
    def check_name(self, key, name):
        if name:
            return name
        raise ValueError("Must have a name")
    
    @validates('age')
    def check_age(self, key, age):
        if (7 < age < 19):
            return age
        raise ValueError("Age must be between 8 and 18")
    
    
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    # Add relationships

    activity = db.relationship('Activity', back_populates = 'signups')
    camper = db.relationship('Camper', back_populates='signups')
    
    # Add serialization rules
    serialize_rules=('-activity.signups' , '-camper.signups')
    
    # Add validation
    @validates('time')
    def check_time(self, key, time):
        if (0 <= time <= 23):
            return time
        raise ValueError('Time must be between 0 and 23.')
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
