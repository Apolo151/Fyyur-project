from config import *
# there is a many to many relationship between artists and venues
# and since there are additional columns not just the foreign key columns
# i define an association Model (Show)
# understood here:
#<https://stackoverflow.com/questions/30406808/flask-sqlalchemy-difference-between-association-model-and-association-table-fo>


class Show(db.Model):
  __tablename__='shows'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
  start_time = db.Column(db.DateTime(timezone=True), nullable=False)
  venue = db.relationship('Venue', backref=db.backref('venues'))
  artist = db.relationship('Artist', backref=db.backref('artists'))
  

# there is a many to many relationship between genres and artists 
# and there is a many to many relationship between genres and venues
# so i define an association table for each relationship (venue_genres),(artist_genres)

venue_genres = db.Table('venue_genres',
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

artist_genres = db.Table('artist_genres',
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

# there is a one to one relationship between Venue and seeking_talent_description
# there is a one to one relationship between Artist and seeking_venues_description
# making a model for each the venues_seeking_talent description and artist_seeking_venues description

class Venues_seeking_talent(db.Model):
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
    description = db.Column(db.String(), nullable = False)

class Artists_seeking_venues(db.Model):
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
    description = db.Column(db.String(), nullable = False)

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), unique=True, nullable=False )
    phone = db.Column(db.String(120), unique=True, nullable=True)
    image_link = db.Column(db.String(500), unique=True, nullable=True)
    facebook_link = db.Column(db.String(120), unique=True, nullable=True)
    website_link = db.Column(db.String, unique=True, nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.relationship('Venues_seeking_talent', backref=db.backref('venues'))
    shows = db.relationship('Show', backref=db.backref('venues'))
    genres = db.relationship('Genre',secondary= venue_genres,
    backref=db.backref('venues', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=True)
    genres = db.relationship('Genre', secondary=artist_genres,
    backref=db.backref('artists', lazy=True))
    image_link = db.Column(db.String(500), unique=True, nullable=True)
    facebook_link = db.Column(db.String(120), unique=True, nullable=True)
    website_link = db.Column(db.String, unique=True, nullable=True)
    seeking_venues = db.Column(db.Boolean, default=False)
    seeking_description = db.relationship('Artists_seeking_venues', backref=db.backref('artists'))
    shows = db.relationship('Show', backref=db.backref('artists'))
   
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# making a genres model to store genres
class Genre(db.Model):
  __tablename__='genres'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable =False, unique=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
