from sqlalchemy.orm import backref
from app import db


artist_genres = db.Table('artist_genres',
  db.Column('Artist', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
  db.Column('genre', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
)


venue_genres = db.Table('venue_genres',
  db.Column('Venue', db.Integer, db.ForeignKey('Artist.id'), primary_key=True),
  db.Column('genre', db.Integer, db.ForeignKey('genre.id'), primary_key=True),
)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venues', lazy='joined'))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String())
    looking_for_talents = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.looking_for_talents} {self.shows}>.'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artists', lazy='joined'))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String())
    looking_for_venues = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.looking_for_venues} {self.shows}>.'


class Show(db.Model):
    _tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<Show {self.id} {self.venue_id} {self.artist_id} {self.start_time}>.'


class Genre(db.Model):
  __tablename__ = 'genre'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), unique=True, nullable=False)

  def __repr__(self):
      return f'<Genre {self.id} {self.name}>.'
