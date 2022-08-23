#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
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
from flask import current_app
import config
from config import *
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import func
from models import db, Venue, Artist, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)
#migrate.init_app(app, db)



# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
 



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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  group_by_location = {}
  current_time = datetime.now()
  for venue in venues:
    location = venue.city + '-' + venue.state
    venue.num_upcoming_shows = Show.query.filter(
          Show.venue_id == venue.id,
          Show.start_time > current_time,
      ).count()
    if location in group_by_location.keys():
          group_by_location[location].venues.append(venue)
    else:
        group_by_location[location] = {
            'city': venue.city,
            'state': venue.state,
            'venues': [venue]
        }
  return render_template('pages/venues.html', areas=group_by_location.values())
 

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  current_time = datetime.now()
  search_operation = Venue.query.filter(db.or_(Venue.name.ilike('%' + search_term + '%'), Venue.location == search_term))#the result of the query is case-insensitive
  venues = search_operation.all()
  for venue in venues:
        venue.num_upcoming_shows = Show.search_operation.filter(
            Show.venue_id == venue.id,
            Show.start_time > current_time,
        ).count()
  response = {
      "count": search_operation.count(),
      "data": venues,
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  current_time = datetime.now()
  venue = Venue.query.get(venue_id)
  print(venue)
  if not venue:       
      return redirect(url_for('index'))#if there is no venue data to display, redirect to index page
  else:
      past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()  
      past_shows = []#initializes the list
      past_shows_count = 0#initializes the count
      upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show. start_time>datetime.now()).all()  
      upcoming_shows = []
      upcoming_shows_count = 0
      

      data = {
          "id": venue_id,
          "name": venue.name,
          "genres": [venue.genres],
          "address": venue.address,
          "city": venue.city,
          "state": venue.state,          
          "phone": venue.phone,
          "website": venue.website,
          "facebook_link": venue.facebook_link,
          "seeking_talent": venue.seeking_talent,
          "seeking_description": venue.seeking_description,
          "image_link": venue.image_link,
          "past_shows": past_shows,
          "past_shows_count": past_shows_count,
          "upcoming_shows": upcoming_shows,
          "upcoming_shows_count": upcoming_shows_count
      }#extracts data from the venues table
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
  form = VenueForm(meta={'csrf': False})
  if form.validate_on_submit():
    try:
      venue = Venue(name=request.form.get('name'),
                    city=request.form.get('city'),
                    state=request.form.get('state'),
                    address=request.form.get('address'),
                    phone=request.form.get('phone'),
                    genres=request.form.getlist('genres'),
                    image_link=request.form.get('image_link'),
                    website=request.form.get('website'),
                    facebook_link=request.form.get('facebook_link'),
                    seeking_talent=request.form.get('seeking_venue') != None,
                    seeking_description=request.form.get('seeking_description'))
      
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    print(form.errors)
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')


  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue = Venue.query.get(venue_id)

  try:
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  return jsonify({"redirect_to": url_for('index')})  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
   return render_template('pages/artists.html', artists=Artist.query.all())
  #artists = Artist.query.order_by(Artist.name).all()
  #data = []
  #for artist in artists:
      #data.append({
          #"id": Artist.id,
          #"name": Artist.name
      #})
  #return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  current_time = datetime.now()
  search_operation = Artist.query.filter(db.or_(Artist.name.ilike('%' + search_term + '%'), Artist.location == search_term))#the result of the query is case-insensitive
  artists = search_operation.all()
  for artist in artists:
        artist.num_upcoming_shows = Show.search_operation.filter(
            Show.artist_id == artist.id,
            Show.start_time > current_time,
        ).count()
  response = {
      "count": search_operation.count(),
      "data": artists,
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)
  

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  current_time = datetime.now()
  artist = Artist.query.get(artist_id)
  #venue = Venue.query.get(venue_id)
  print(artist)
  if not artist:       
      return redirect(url_for('index'))#if there is no venue data to display, redirect to index page
  else:
      past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all() 
      past_shows = []#initializes the list
      past_shows_count = 0#initializes the count
      upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).all() 
      upcoming_shows = []
      upcoming_shows_count = 0
      #for show in upcoming_shows_query:        
        #upcoming_shows_count += 1
        #upcoming_shows.append({
            #"venue_id": show.venue_id,
            #"venue_name": show.venue.name,
            #"venue_image_link": show.venue.image_link,
            #"start_time": format_datetime(str(show.start_time))#stringifies the start_time
        #})
      #for show in past_shows_query:
        #past_shows_count += 1
        #past_shows.append({
            #"venue_id": show.venue_id,
            #"venue_name": show.venue.name,
            #"venue_image_link": show.venue.image_link,
           # "start_time": format_datetime(str(show.start_time))
        #})

      data = {
          "id": artist_id,
          "name": artist.name,
          "genres": [artist.genres],
          "city": artist.city,
          "state": artist.state,          
          "phone": artist.phone,
          "genres":artist.genres,
          "website": artist.website,
          "facebook_link": artist.facebook_link,
          "seeking_venue": artist.seeking_venue,
          "seeking_description": artist.seeking_description,
          "image_link": artist.image_link,
          "past_shows": past_shows,
          "past_shows_count": past_shows_count,
          "upcoming_shows": upcoming_shows,
          "upcoming_shows_count": upcoming_shows_count
      }#extracts data from the venues table
  return render_template('pages/show_artist.html', artist=data)
   

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
    
  form = ArtistForm()
  form.name.default = artist.name
  form.city.default = artist.city
  form.state.default = artist.state
  form.phone.default = artist.phone
  form.genres.default = artist.genres
  form.image_link.default = artist.image_link
  form.website.default = artist.website
  form.facebook_link.default = artist.facebook_link
  form.seeking_venue.default = artist.seeking_venue
  form.seeking_description.default = artist.seeking_description
  form.process()

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existin
  form = ArtistForm(meta={'csrf': False})
  if form.validate_on_submit():
    try:
        VenueGenre.query.filter(VenueGenre.venue_id == venue_id).delete()

        venue = Venue.query.get(venue_id)

        is_seeking_talent_checked = request.form.get('seeking_talent') != None
        seeking_talent = is_seeking_talent_checked if venue.seeking_talent != is_seeking_talent_checked else venue.seeking_talent

        venue.name = request.form.get('name', venue.name)
        venue.city = request.form.get('city', venue.city)
        venue.state = request.form.get('state', venue.state)
        venue.phone = request.form.get('phone', venue.phone)
        venue.image_link = request.form.get('image_link', venue.image_link)
        venue.website = request.form.get('website', venue.website)
        venue.facebook_link = request.form.get('facebook_link', venue.facebook_link)
        venue.seeking_talent = seeking_talent
        venue.seeking_description = request.form.get('seeking_description',
                                                     venue.seeking_description)

        for genre_name in request.form.getlist('genres'):
            venue.genres.append(VenueGenre(genre_name=genre_name))

        db.session.commit()

    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
  else:
    print(form.errors)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')


    return redirect(url_for('show_venue', venue_id=venue_id))


   
  
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(meta={'csrf': False})
  if form.validate_on_submit():  
      try:
        venue = Venue.query.get(venue_id)

        is_seeking_talent_checked = request.form.get('seeking_talent') != None
        seeking_talent = is_seeking_talent_checked if venue.seeking_talent != is_seeking_talent_checked else venue.seeking_talent

        venue.name = request.form.get('name', venue.name)
        venue.city = request.form.get('city', venue.city)
        venue.state = request.form.get('state', venue.state)
        venue.phone = request.form.get('phone', venue.phone)
        venue.genres = request.form.getlist('genres', venue.genres)
        venue.image_link = request.form.get('image_link', venue.image_link)
        venue.website = request.form.get('website', venue.website)
        venue.facebook_link = request.form.get('facebook_link', venue.facebook_link)
        venue.seeking_talent = seeking_talent
        venue.seeking_description = request.form.get('seeking_description', venue.seeking_description)

        db.session.add(venue)
        db.session.commit()

      except:
          db.session.rollback()
          print(sys.exc_info())
      finally:
          db.session.close()

    
  else:
    print(form.errors)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(meta={'csrf': False})
  if form.validate_on_submit():
    try:
      artist = Artist(name=request.form.get('name'),
                  city=request.form.get('city'),
                  state=request.form.get('state'),
                  phone=request.form.get('phone'),
                  genres=request.form.getlist('genres'),
                  image_link=request.form.get('image_link'),
                  website=request.form.get('website'),
                  facebook_link=request.form.get('facebook_link'),
                  seeking_venue=request.form.get('seeking_venue') != None,
                  seeking_description=request.form.get('seeking_description'))  
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    finally:
      db.session.close()
  else:
    print(form.errors)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []#initialize
  shows = Show.query.all()
  
  for show in shows:
      data.append({
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": format_datetime(str(show.start_time))#stringify
      })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(meta={'csrf': False})
  
  
  venue_id = form.venue_id.data
  artist_id = form.artist_id.data
  start_time = form.start_time.data
  if form.validate_on_submit():
    
    try:
        new_show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
  else:
    print(form.errors)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')


  

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
