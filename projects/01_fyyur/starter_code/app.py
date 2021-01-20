#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from models import *
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app,db)
# db.expire_on_commit=False


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. 

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
  data = list()
  locations = Location.query.all()

  for location in locations:
      entry = dict()
      entry['city']=location.city
      entry['state']=location.state
      venues_list=list()
      for venue in location.venues:
        venues_list.append({'id': venue.id,
                            'name': venue.name,
                          })
      entry['venues']=venues_list
      data.append(entry)
     

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  #results = Venue.query.filter(Venue.name.contains(search_term)).all() # Case sensitive match
  results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all() # Ignore Case match

  response={
    "count": len(results),
    "data": [{
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": 1,
    } for result in results]
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  current_time = datetime.utcnow()

  past_shows = Show.query.join(Venue,Venue.id==Show.venue_id).filter(Venue.id==venue.id,Show.start_time<=current_time).order_by(Show.start_time).all()
  upcoming_shows = Show.query.join(Venue,Venue.id==Show.venue_id).filter(Venue.id==venue.id,Show.start_time>current_time).order_by(Show.start_time).all()
  data={
    "id": venue_id,
    "name": venue.name,
    "genres": [g.name for g in venue.genres],
    "address": venue.address,
    "city": venue.location.city,
    "state": venue.location.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [{
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    } for show in past_shows],
    "upcoming_shows": [{
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    } for show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
  name = request.form['name']
  address=request.form['address']
  phone=request.form['phone']
  facebook_link=request.form['facebook_link']
  website_link = request.form['website_link']
  image_link = request.form['image_link']
  
  if request.form.get('seeking_talent'):
    seeking_talent=True
    seeking_description = request.form['seeking_description']
  else:
    seeking_talent=False
    seeking_description=None
  
  city =request.form['city']
  state =request.form['state']
  location = Location.query.filter(Location.city==city,Location.state==state).first()
  if location is None:
    location  = Location(city=city,state=state)

  genres_list = request.form.getlist('genres')
  genres=list()
  for genre in genres_list:
    genres.append(Genre.query.filter(Genre.name==genre).first())


  error = False

  try:
    venue = Venue(name=name,address=address,phone=phone,
    facebook_link=facebook_link,location=location,genres=genres,
    website_link=website_link,image_link=image_link,seeking_talent=seeking_talent,seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    venue_id = venue.id
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + name + ' could not be listed.')
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)
  else:
    flash('Venue ' + name + ' was successfully listed!')

  return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.filter(Venue.id==venue_id).first_or_404()
  venue_id=venue.id
  error = False
  
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print('error','#'*100)
    error = True
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue  could not be deleted.')
    return jsonify({'success':False})
  else:
    flash('Venue  was successfully Delete!')
    return jsonify({'success':True})
  
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term=request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  response={
    "count": len(artists),
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": 0,
    } for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter(Artist.id==artist_id).first_or_404()
  current_time = datetime.utcnow()
  past_shows = Show.query.join(Artist, Artist.id==Show.artist_id).filter(Show.start_time<=current_time,Artist.id==artist.id).order_by(Show.start_time).all()
  upcoming_shows = Show.query.join(Artist,Artist.id==Show.artist_id).filter(Show.start_time>current_time,Artist.id==artist.id).order_by(Show.start_time).all()
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": [genre.name for genre in artist.a_genres],
    "city": artist.a_location.city,
    "state": artist.a_location.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [{
      "venue_id": show.venue.id,
      "venue_name": show.venue.name ,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    } for show in past_shows],
    "upcoming_shows": [{
      "venue_id": show.venue.id,
      "venue_name": show.venue.name ,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    } for show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.phone.data = artist.phone
  form.city.data= artist.a_location.city
  form.state.data= artist.a_location.state
  form.genres.data = [genre.name for genre in artist.a_genres]
  form.facebook_link.data  = artist.facebook_link
  form.image_link.data  = artist.image_link
  form.website_link.data  = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  artist.name = request.form['name']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.website_link = request.form['website_link']
  artist.image_link = request.form['image_link']
  
  location = Location.query.filter(Location.city==request.form['city'],Location.state==request.form['state']).first()
  if location is None:
    location = Location(city=request.form['city'],state=request.form['state'])
  artist.a_location = location

  if request.form.get('seeking_venue'):
    artist.seeking_venue = True
    artist.seeking_description = request.form['seeking_description']
  else:
    artist.seeking_venue = False
    artist.seeking_description = None

  genres_list = request.form.getlist('genres')
  genres = list()
  for genre in genres_list:
    genres.append(Genre.query.filter(Genre.name==genre).first())
  artist.a_genres = genres

  try:
    db.session.commit()
    artist_id=artist.id
    flash('Artist ' + request.form['name'] + ' was successfully Updated!')
  except:
    db.session.rollback()
    flash('Error: Artist ' + request.form['name'] + ' could not be Updated ')
  finally:
    db.session.close()

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
  venue = Venue.query.get(venue_id)
  form.name.data=venue.name
  form.city.data = venue.location.city
  form.state.data = venue.location.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = [g.name for g in venue.genres] 
  form.seeking_talent.data = venue.seeking_talent
  if venue.seeking_talent:
    form.seeking_description.data = venue.seeking_description
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  name = request.form['name']
  address=request.form['address']
  phone=request.form['phone']
  facebook_link=request.form['facebook_link']
  website_link = request.form['website_link']
  image_link = request.form['image_link']

  if request.form.get('seeking_talent'):
    seeking_talent=True
    seeking_description = request.form['seeking_description']
  else:
    print('no'*100)
    seeking_talent=False
    seeking_description=None
  

  city =request.form['city']
  state =request.form['state']
  location = Location.query.filter(Location.city==city,Location.state==state).first()
  if location is None:
    location  = Location(city=city,state=state)

  genres_list = request.form.getlist('genres')
  genres=list()
  for genre in genres_list:
    genres.append(Genre.query.filter(Genre.name==genre).first())

  error = False
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  print(venue)

  try:
    venue.name=name
    venue.address=address
    venue.phone=phone,
    venue.facebook_link=facebook_link
    venue.location=location
    venue.genres=genres
    venue.website_link=website_link
    venue.image_link=image_link
    venue.seeking_talent=seeking_talent
    venue.seeking_description=seeking_description
    db.session.commit()
    
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' +name + ' could not be updated.')
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)
  else:
    flash('Venue ' + name + ' was successfully Updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  artist = Artist()
  artist.name = request.form['name']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.website_link = request.form['website_link']
  artist.image_link = request.form['image_link']
  location = Location.query.filter(Location.city==request.form['city'],Location.state==request.form['state']).first()
  if location is None:
    location = Location(city=request.form['city'],state=request.form['state'])
  artist.a_location = location

  if request.form.get('seeking_venue'):
    artist.seeking_venue = True
    artist.seeking_description = request.form['seeking_description']
  else:
    artist.seeking_venue = False
    artist.seeking_description = None

  genres_list = request.form.getlist('genres')
  genres = list()
  for genre in genres_list:
    genres.append(Genre.query.filter(Genre.name==genre).first())
  artist.a_genres = genres

  try:
    db.session.add(artist)
    db.session.commit()
    artist_id=artist.id
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('Error: Artist ' + request.form['name'] + ' was not created ')
  finally:
    db.session.close()

  return redirect(url_for('show_artist',artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()

  data=[{
    "venue_id": show.venue.id,
    "venue_name": show.venue.name,
    "artist_id": show.artist.id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
  } for show in shows]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  venue = Venue.query.get(request.form['venue_id'])
  artist = Artist.query.get(request.form['artist_id'])
  show = Show(venue=venue,artist=artist,start_time=request.form['start_time'])

  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Error: Show could not be created!')

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
