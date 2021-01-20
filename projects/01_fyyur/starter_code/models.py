from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
  __tablename__='Show'
  id = db.Column(db.Integer,primary_key=True)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'))
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'))
  start_time = db.Column(db.DateTime)
  upcomin = db.Column(db.Boolean,default=True)


class Location(db.Model):
    __tablename__ = 'Location'

    id = db.Column(db.Integer,primary_key=True)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    venues = db.relationship('Venue',backref=db.backref('location',cascade='all,delete'),cascade='all,delete')
    artists = db.relationship('Artist',backref=db.backref('a_location',cascade='all,delete'),cascade='all,delete')

Venue_Genre= db.Table('Venue_Genre',
              db.Column('venue_id',db.Integer,db.ForeignKey('Venue.id'),primary_key=True),
              db.Column('genre_id',db.Integer,db.ForeignKey('Genre.id'),primary_key=True))
              
Artist_Genre= db.Table('Artist_Genre',
              db.Column('artist_id',db.Integer,db.ForeignKey('Artist.id'),primary_key=True),
              db.Column('genre_id',db.Integer,db.ForeignKey('Genre.id'),primary_key=True))
              

class Genre(db.Model):
  __tablename__ ='Genre'

  id = db.Column(db.Integer,primary_key=True)
  name = db.Column(db.String(),nullable=False)
  venues = db.relationship('Venue',secondary=Venue_Genre,backref='genres')
  artists = db.relationship('Artist',secondary=Artist_Genre,backref='a_genres')



class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    #city = db.Column(db.String(120))
    #state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500),default="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60")
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    location_id = db.Column(db.Integer,db.ForeignKey('Location.id'),nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description =db.Column(db.Text)
    shows = db.relationship('Show',backref='venue')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500),default="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80")
    facebook_link = db.Column(db.String(120))
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description =db.Column(db.Text)
    location_id = db.Column(db.Integer,db.ForeignKey('Location.id'),nullable=False)
    shows = db.relationship('Show',backref='artist')

    def __repr__(self):
      return f'<Artist : id={self.id} name:{self.name}>'
