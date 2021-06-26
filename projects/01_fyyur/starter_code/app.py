#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from enum import unique
import json
from os import abort
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate, migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  venue = Venue.query.get(venue_id)
  # abort 404 if venue not found in database
  if not venue:
    app.register_error_handler(404, not_found_error)
    return app

  # get list genres' name from the venue's genres opjects
  genres = [genre.name for genre in venue.genres]

  # get list of the venue's past shows
  pastShows = []
  pastShows_count = 0
  for show in Show.query.filter(Show.venue_id==venue_id, Show.start_time<datetime.now()).all():
    pastShow_dict={}
    pastShow_dict['artist_id'] = show.artist_id
    pastShow_dict['artist_name'] = Artist.query.get(show.artist_id).name
    pastShow_dict['artist_image_link'] = Artist.query.get(show.artist_id).image_link
    pastShow_dict['start_time'] = show.start_time.isoformat()
    pastShows.append(pastShow_dict)
    pastShows_count += 1

  # get list of the venue's upcomming shows
  upcomingShows = []
  upcomingShows_count = 0
  for show in Show.query.filter(Show.venue_id==venue_id, Show.start_time>datetime.now()).all():
    upcomingShow_dict={}
    upcomingShow_dict['artist_id'] = show.artist_id
    upcomingShow_dict['artist_name'] = Artist.query.get(show.artist_id).name
    upcomingShow_dict['artist_image_link'] = Artist.query.get(show.artist_id).image_link
    upcomingShow_dict['start_time'] = show.start_time.isoformat()
    upcomingShows.append(upcomingShow_dict)
    upcomingShows_count += 1

  data={
    "id": venue_id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.looking_for_talents,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": pastShows_count,
    "upcoming_shows_count": upcomingShows_count,
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  if form.validate():
    error = False
    # insert form data as a new Venue record in the db, instead
    try:
      # genre table is already populated with genres data
      genresList = Genre.query.filter(Genre.name.in_(form.genres.data)).all()
      venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        looking_for_talents=form.seeking_talent.data,
        seeking_description=form.seeking_description.data
      )
      venue.genres = genresList
      db.session.add(venue)
      db.session.commit()

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
        db.session.close()

    if not error:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      
    return render_template('pages/home.html')
  
  # flash form validation error messages if form is not valid
  for _, error in form.errors.items():
    flash(error[0], category='error')

  return(render_template('forms/new_venue.html', form=form))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=[]

  for artist in Artist.query.all():
    artist_dict = {}
    artist_dict['id'] = artist.id
    artist_dict['name'] = artist.name
    data.append(artist_dict)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # request the requiredartist from the database
  artist = Artist.query.get(artist_id)
  # abort 404 if artist not found in database
  if not artist:
    app.register_error_handler(404, not_found_error)
    return app

  # get list genres' name from the artist's genres opjects
  genres = [genre.name for genre in artist.genres]

  # get list of the artist's past shows
  pastShows = []
  pastShows_count = 0
  for show in Show.query.filter(Show.artist_id==artist_id, Show.start_time<datetime.now()).all():
    pastShow_dict={}
    pastShow_dict['venue_id'] = show.venue_id
    pastShow_dict['venue_name'] = Venue.query.get(show.venue_id).name
    pastShow_dict['venue_image_link'] = Venue.query.get(show.venue_id).image_link
    pastShow_dict['start_time'] = show.start_time.isoformat()
    pastShows.append(pastShow_dict)
    pastShows_count += 1

  # get list of the artist's upcomming shows
  upcomingShows = []
  upcomingShows_count = 0
  for show in Show.query.filter(Show.artist_id==artist_id, Show.start_time>datetime.now()).all():
    upcomingShow_dict={}
    upcomingShow_dict['venue_id'] = show.venue_id
    upcomingShow_dict['venue_name'] = Venue.query.get(show.venue_id).name
    upcomingShow_dict['venue_image_link'] = Venue.query.get(show.venue_id).image_link
    upcomingShow_dict['start_time'] = show.start_time.isoformat()
    upcomingShows.append(upcomingShow_dict)
    upcomingShows_count += 1

  data={
    "id": artist_id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.looking_for_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastShows,
    "upcoming_shows": upcomingShows,
    "past_shows_count": pastShows_count,
    "upcoming_shows_count": upcomingShows_count,
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm()
  if form.validate():
    error = False
    # insert form data as a new Artist record in the db, instead
    try:
      # genre table is already populated with genres data
      genresList = Genre.query.filter(Genre.name.in_(form.genres.data)).all()
      artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        looking_for_venues=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
      )
      artist.genres = genresList
      db.session.add(artist)
      db.session.commit()

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
        db.session.close()

    if not error:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      
    return render_template('pages/home.html')
  
  # flash form validation error messages if form is not valid
  for _, error in form.errors.items():
    flash(error[0], category='error')
  return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  for show in Show.query.all():
    show_dict = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.isoformat()
    }
    data.append(show_dict)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm()
  if form.validate():
    error = False
    # validate the venue ID
    if not Venue.query.get(form.venue_id.data):
      flash('Venue ID is not valid', category='error')
      return render_template('forms/new_show.html', form=form)

    # validate the artist ID
    if not Artist.query.get(form.artist_id.data):
      flash('Artist ID is not valid', category='error')
      return render_template('forms/new_show.html', form=form)

    # insert form data as a new Show record in the db, instead
    try:
      show = Show(
        venue_id=form.venue_id.data,
        artist_id=form.artist_id.data,
        start_time=form.start_time.data)

      # append show to the artist and the venue
      show.venue = Venue.query.get(form.venue_id.data)
      show.artist = Artist.query.get(form.artist_id.data)

      db.session.add(show)
      db.session.commit()

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())

    finally:
        db.session.close()

    if not error:
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    else:
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
      
    return render_template('pages/home.html')

  # flash form validation error messages if form is not valid
  for _, error in form.errors.items():
    flash(error[0], category='error')
  return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
