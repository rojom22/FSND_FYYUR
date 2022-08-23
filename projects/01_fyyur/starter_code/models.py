
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    location = db.column_property(city + ", " + state)
    #genres = db.Column(db.MutableList.as_mutable(PickleType()), default = [])
    #genres = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))    
    website = db.Column(db.String(120))#not every venue is supposed to have a website
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(280))#280 like a tweet, some might have specific details
    shows = db.relationship('Show', backref='venue', lazy=True)

   
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    location = db.column_property(city + ", " + state)# city and state are grouped 
    #genres = db.Column(db.MutableList.as_mutable(PickleType), default = [])
    #genres = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))    
    website = db.Column(db.String(120))#not every venue is supposed to have a website
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)#this column was the source of mistake, corrected it
    seeking_description = db.Column(db.String(280))#280 like a tweet, some might have specific details
    shows = db.relationship('Show', backref='artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)












    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.