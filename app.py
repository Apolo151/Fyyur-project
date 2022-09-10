#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
from sqlalchemy import Sequence
import sys
from models import *
import pytz
from config import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# moved App Config to config.py

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# moved Models to models.py

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  data =[]
  # finding every unique city,state in the venues table
  cities_states = Venue.query.with_entities(Venue.city,Venue.state).distinct()
  # for each city,state find related venues
  for city_state in cities_states :
    venues = Venue.query.filter(Venue.city == city_state.city,Venue.state == city_state.state).all()
    city_venues = []
    #for each venue append venue data to city_venues list 
    for venue in venues:
      city_venues.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.today()).all())
      })
    # append city, state and venues to data list
    data.append({
      "city": city_state.city,
      "state": city_state.state,
      "venues": city_venues
    })   
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # getting the user input
  search_term = request.form.get('search_term', '')
  # searching through venues table by venue name
  venues = Venue.query.filter(Venue.name.ilike('%'+ search_term +'%')).all()
  # getting the total results number
  count = Venue.query.filter(Venue.name.ilike('%'+ search_term +'%')).count()
  response = {
      "count": count,
      "data": venues
    }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows = []
  upcoming_shows = []
  genres_names = []
  
  # getting the venue object
  venue = Venue.query.get(venue_id)
  # getting the venue's genres names
  for genre in venue.genres:
    genres_names.append(genre.name)

  # making the datetime.today aware to be able to compare it 
  # understood here:https://stackoverflow.com/questions/7065164/how-to-make-an-unaware-datetime-timezone-aware-in-python
  aware_today = pytz.utc.localize(datetime.today())
  if len(venue.shows) != 0:
    for show in venue.shows:
      # if the show start time is before or equal to today append it to past_shows list
      if show.start_time <= aware_today:
        past_shows.append({    
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": str(show.start_time)
        })
        # else append it to upcoming_shows list
      else:
        upcoming_shows.append({    
          "artist_id": show.artist_id,
          "artist_name": show.artists.name,
          "artist_image_link": show.artist.image_link,
         "start_time": str(show.start_time)
      })
  
  # if the venue is seeking talent get the seeking description 
  # else set the seeking description to None
  if venue.seeking_talent == True:
    desc = venue.seeking_description[0].description
  else:
    desc = None
  data = {
    "id": venue_id,
    "name": venue.name,
    "genres": genres_names,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": desc,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    form = VenueForm(request.form)
    # checking if fields where left empty
    # if a value equals an empty string set it to None(NULL)
    # else set it to the value the user entered
    if form.phone.data == '':
      phone = None
    else:
      phone = form.phone.data

    if form.facebook_link.data == '':
      facebook_link = None
    else:
      facebook_link = form.facebook_link.data

    if form.image_link.data =='':
      image_link = None
    else:
      image_link = form.image_link.data

    if form.website_link.data == '':
      website_link = None
    else:
      website_link = form.website_link.data
    # did that to be able to have null values and unique values in the table
    # and let the user be able to leave unrequired fields empty
    # because if the column is unique it can't have multiple empty strings
    # creating a new venue with the form data
    venue = Venue(name= form.name.data, city= form.city.data, state= form.state.data,
    address= form.address.data, phone= phone, facebook_link= facebook_link,
    image_link= image_link, seeking_talent= form.seeking_talent.data,
    website_link= website_link)
    # if the venue is seeking talent get the seeking description field data 
    # and add the description child to the venue parent
    if form.seeking_talent.data == True:
      seeking_desc = Venues_seeking_talent(description=form.seeking_description.data)
      venue.seeking_description = [seeking_desc]
    # looping through genres from user input
    for genre in form.genres.data :
      #checking if genre already exists in database 
      genre_exist = Genre.query.filter_by(name=genre).first()
      if genre_exist:
        #if exists add it to genres of the venue
        venue.genres.append(genre_exist)
      else:
        # else make new genre and add it to genres of the venue
        new_genre = Genre(name=genre)
        venue.genres.append(new_genre)    
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    # getting the venue by id
    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    # delete the seeking_talent_description 
    Venues_seeking_talent.query.filter(Venues_seeking_talent.venue_id == venue_id).delete()
    # deleting the venue's shows from the shows table
    Show.query.filter(Show.venue_id == venue.id).delete()
    # deleting the venue 
    db.session.delete(venue)
    db.session.commit()
    flash('Venue '+ venue.name +' was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("An error ocurred. Venue "+ venue.name +" couldn't be deleted")
  finally:
    db.session.close()
  return redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  # getting all the artists
  artists = Artist.query.all()
  # for each artist in the artists list add the artist to the data list
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artists_data = []
  # getting the user input
  search_term = request.form.get('search_term')
  # searching through the artists table by name
  artists = Artist.query.filter(Artist.name.ilike('%'+ search_term +'%')).all()
  # getting the total results number
  count = Artist.query.filter(Artist.name.ilike('%'+ search_term +'%')).count()
  for artist in artists:
    artists_data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_show": len(Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.today()).all())
    })
  response = {
    "count": count,
    "data": artists_data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  past_shows = []
  upcoming_shows = []
  genres_names = []

  # getting the artist object
  artist = Artist.query.get(artist_id)
  # getting the artist's genres names
  for genre in artist.genres:
    genres_names.append(genre.name)

  # making the datetime.today aware to be able to compare it 
  # understood here:https://stackoverflow.com/questions/7065164/how-to-make-an-unaware-datetime-timezone-aware-in-python
  aware_today = pytz.utc.localize(datetime.today())
  if len(artist.shows) != 0:
    for show in artist.shows:
      # if the show start time is before or equal to today append it to past_shows list
      if show.start_time <= aware_today:
        past_shows.append({    
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })
        # else append it to upcoming_shows list
      else:
        upcoming_shows.append({    
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
      })

  # if the artist is seeking venues get the seeking description 
  # else set the seeking description to None
  if artist.seeking_venues == True:
    desc = artist.seeking_description[0].description
  else:
    desc = None
  data = {
    "id": artist_id,
    "name": artist.name,
    "genres": genres_names,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venues,
    "seeking_description": desc,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_genres = []
  # getting the artist by id
  artist = Artist.query.get(artist_id)
  # populating the form fields
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.seeking_venues.data = artist.seeking_venues
  form.website_link.data = artist.website_link
  for genre in artist.genres:
    artist_genres.append(genre.name)
  form.genres.data = artist_genres
  if artist.seeking_venues:
    form.seeking_description.data = artist.seeking_description[0].description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm(request.form)
    # checking if fields where left empty
    # if a value equals an empty string set it to None(NULL)
    # else set it to the value the user entered
    if form.phone.data == '':
      phone = None
    else:
      phone = form.phone.data

    if form.facebook_link.data == '':
      facebook_link = None
    else:
      facebook_link = form.facebook_link.data

    if form.image_link.data =='':
      image_link = None
    else:
      image_link = form.image_link.data

    if form.website_link.data == '':
      website_link = None
    else:
      website_link = form.website_link.data
    # getting the artist by id
    artist = Artist.query.get(artist_id)
    # updating the artist's data
    artist.name= form.name.data
    artist.city= form.city.data
    artist.state= form.state.data
    artist.phone= phone
    artist.facebook_link= facebook_link
    artist.image_link= image_link
    artist.seeking_venues= form.seeking_venues.data
    artist.website_link= website_link
    # if the artist is seeking venues get the seeking description field data 
    # and add the description child to the artist parent
    artist_seeking_description = Artists_seeking_venues.query.get(artist_id)
    # if the artist had a seeking_description before replace it with the new form seeking_description
    if form.seeking_venues.data == True and artist_seeking_description:
      artist.seeking_description[0].description = form.seeking_description.data
    elif form.seeking_venues.data == True :
      seeking_desc = Artists_seeking_venues(description = form.seeking_description.data)
      artist.seeking_description = [seeking_desc]
    elif form.seeking_venues.data == False and artist_seeking_description:
      db.session.delete(artist_seeking_description)
    # clearing artist's genres
    artist.genres = []
    # looping through genres from user input
    for genre in form.genres.data :
      #checking if genre already exists in database 
      genre_exist = Genre.query.filter_by(name=genre).first()
      if genre_exist:
        # if exists add it to genres of the artist
        artist.genres.append(genre_exist)
      else:
        # else make new genre and add it to genres of the artist
        new_genre = Genre(name=genre)
        artist.genres.append(new_genre)    
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue_genres = []
  # getting the venue by id
  venue = Venue.query.get(venue_id)
  # populating the form fields
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_talent
  form.website_link.data = venue.website_link
  for genre in venue.genres:
    venue_genres.append(genre.name)
  form.genres.data = venue_genres
  if venue.seeking_talent:
    form.seeking_description.data = venue.seeking_description[0].description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm(request.form)
    # checking if fields where left empty
    # if a value equals an empty string set it to None(NULL)
    # else set it to the value the user entered
    if form.phone.data == '':
      phone = None
    else:
      phone = form.phone.data

    if form.facebook_link.data == '':
      facebook_link = None
    else:
      facebook_link = form.facebook_link.data

    if form.image_link.data =='':
      image_link = None
    else:
      image_link = form.image_link.data

    if form.website_link.data == '':
      website_link = None
    else:
      website_link = form.website_link.data
    # getting the venue by id
    venue = Venue.query.get(venue_id)
    # updating the venue's data
    venue.name= form.name.data
    venue.city= form.city.data
    venue.state= form.state.data
    venue.address= form.address.data
    venue.phone= phone
    venue.facebook_link= facebook_link
    venue.image_link= image_link
    venue.seeking_talent= form.seeking_talent.data
    venue.website_link= website_link
    # if the venue is seeking talent get the seeking description field data 
    # and add the description child to the venue parent
    venue_seeking_description = Venues_seeking_talent.query.get(venue_id)
    # if the venue had a seeking_description before replace it with the new form seeking_description
    if form.seeking_talent.data == True and venue_seeking_description:
      venue.seeking_description[0].description = form.seeking_description.data
    elif form.seeking_talent.data == True :
      seeking_desc = Venues_seeking_talent(description = form.seeking_description.data)
      venue.seeking_description = [seeking_desc]
    elif form.seeking_talent.data == False and venue_seeking_description:
      db.session.delete(venue_seeking_description)
    # clearing venue's genres
    venue.genres = []
    # looping through genres from user input
    for genre in form.genres.data :
      #checking if genre already exists in database 
      genre_exist = Genre.query.filter_by(name=genre).first()
      if genre_exist:
        # if exists add it to genres of the venue
        venue.genres.append(genre_exist)
      else:
        # else make new genre and add it to genres of the venue
        new_genre = Genre(name=genre)
        venue.genres.append(new_genre)    
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
  finally:
    db.session.close()
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    # getting the form data
    form = ArtistForm(request.form)
    # checking if fields where left empty
    # if a value equals an empty string set it to None(NULL)
    # else set it to the value the user entered
    if form.phone.data == '':
      phone = None
    else:
      phone = form.phone.data

    if form.facebook_link.data == '':
      facebook_link = None
    else:
      facebook_link = form.facebook_link.data

    if form.image_link.data =='':
      image_link = None
    else:
      image_link = form.image_link.data

    if form.website_link.data == '':
      website_link = None
    else:
      website_link = form.website_link.data
    # creating a new artist with the form data
    artist = Artist(name= form.name.data, city= form.city.data, state= form.state.data, 
    phone= phone, facebook_link= facebook_link, image_link= image_link,
    seeking_venues= form.seeking_venues.data, website_link= website_link)
    # if the artist is seeking venues get the seeking description field data 
      # and add the description child to the artist parent
    if form.seeking_venues.data == True:
      seeking_desc = Artists_seeking_venues(description=form.seeking_description.data)
      artist.seeking_description.append(seeking_desc)
    # looping through genres from user input
    for genre in form.genres.data:
      # checking if genre already exists in the database
      genre_exist = Genre.query.filter_by(name=genre).first()
      if genre_exist:
        # if exists add genre to genres of artist
        artist.genres.append(genre_exist)
      else:
        # else make new genre and add it to genres of artist
        the_genre = Genre(name = genre)
        artist.genres.append(the_genre) 
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # joining shows table with venues and artists tables
  shows = Show.query.join(Artist).join(Venue).all()
  data = []
  # looping through the shows
  for show in shows:
    # appending results to the data list
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
      # called to create new shows in the db, upon submitting new show listing form
      # TODO: insert form data as a new Show record in the db, instead

      # getting the form data
      form = ShowForm(request.form)
      # creating a new show with the form data
      show = Show(venue_id = form.venue_id.data, artist_id = form.artist_id.data,
      start_time = form.start_time.data)
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  except:
      db.session.rollback()
      print(sys.exc_info())
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
  finally:
      db.session.close()
  return render_template('pages/home.html')

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
