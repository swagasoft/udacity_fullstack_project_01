#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_wtf import Form
from sqlalchemy import JSON, null
from forms import *
#----------------------------------------------------------------------------#
# App Config.

#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Genre(db.Model):
  __tablename__ = 'Genre'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())

artist_genre_table = db.Table('artist_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

venue_genre_table = db.Table('venue_genre_table',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.ARRAY(db.String()))
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # genres = db.relationship('Genre',)
    shows  = db.relationship('Show', backref= db.backref('Venue'), lazy=True)

    # genres = db.relationship('Genre', secondary=venue_genre_table, backref=('venue'))

    def __repr__(self) -> str:
       return f'<Venue {self.id}  {self.shows}  >'
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show", backref=db.backref('Artist'), lazy=True)

    def __repr__(self) -> str:
       return f'<Artist {self.id}  {self.name}  >'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = "Show"

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)


  def __repr__(self) -> str:
     return f'<Show {self.artist_id} {self.venue_id}>'
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
  venues = Venue.query.order_by(Venue.state, Venue.city).all()

  venue_data = []
  temp_venue = {}
  prev_city = None
  prev_state = None

  for venue in venues:
    db_data = {
      'id': venue.id, 'name': venue.name, 'num_upcoming_show':len(list(filter(lambda x: x.start_time > datetime.today(),
      venue.shows)))
    }
    if(venue.city == prev_city  and venue.state == prev_state):
      temp_venue['venues'].append(db_data)
    else:
      if prev_city is not null:
        venue_data.append(temp_venue)
        temp_venue['city'] = venue.city
        temp_venue['state'] = venue.state
        temp_venue['venues'] = [db_data]
    prev_city = venue.city
    prev_state = venue.state

  venue_data.append(temp_venue)

  return render_template('pages/venues.html', areas=venue_data)


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
  venue = Venue.query.get(venue_id)
  artist = Artist.query.get(artist_id)

  print('Venue GGGGGGG ', venue)
  print('Venue SHOW ', venue.shows)
  if not venue:
    return render_template(url_for('index'))
  else:
    genres = [genre for genre in venue.genres]
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    now = datetime.now()
    for show in venue.shows:
      if show.start_time > now:
        upcoming_shows_count = upcoming_shows_count + 1
        upcoming_shows.append({
          'artist_id': show.artist_id,
          # 'artist_name': show.artist_name,
          # 'artist_image_link': show.artist_image_link,
          'start_time':format_datetime(str(show.start_time))
        })
      
      if show.start_time < now:
        past_shows_count = past_shows_count + 1
        past_shows.append({
          'artist_id': show.artist_id,
          # 'artist_name': show.artist_name,
          # 'artist_image_link': show.artist_image_link,
          'start_time': format_datetime(str(show.start_time))
        })

    data = {
        'id':venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'genres': genres,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows_count': past_shows_count,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'upcoming_shows_count': upcoming_shows_count,
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
  print('Form data ', request.form)

  try:
    name = request.form['name']
    city =  request.form['city']
    state =  request.form['state']
    address =  request.form['address']
    phone =  request.form['phone']
    image_link =  request.form['image_link']
    genres =  request.form.getlist('genres')
    facebook_link =  request.form['facebook_link']
    website_link =  request.form['website_link']
    seeking_talent =  request.form['seeking_talent']
    seeking_description =  request.form['seeking_description']
    seeking_talent =   True if request.form['seeking_talent'] == 'y' else False


    # TODO: modify data to be the data object returned from db insertion
    new_venue = Venue(name=name, city=city, state=state, address=address,phone=phone,image_link= image_link,genres=genres, facebook_link = facebook_link, website = website_link, seeking_talent=seeking_talent,seeking_description=seeking_description)
    db.session.add(new_venue)
    db.session.commit()
  except Exception as e:
    print('ERRRRRR ', e)
    flash('Error saving ' + request.form['name'] + '!',"error" )
    db.session.rollback()
  finally:
    db.session.close()
    flash('Venue ' + request.form['name'] + ' was successfully listed!',"success")




    # on successful db insert, flash success
    
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
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()

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
  artist_query = db.session.query(Artist).get(artist_id)
  if not artist_query:
    return render_template('error/404.html')
  else:
    genres = [genre for genre in artist_query.genres]
    past_shows = []
    past_shows_count = 0
    upcoming_shows = []
    upcoming_shows_count = 0
    now = datetime.now()

    for show in artist_query.shows:
      if show.start_time > now:
        upcoming_shows_count += 1
        upcoming_shows.append({
          'venue_id': show.venue_id,
          'start_time': format_datetime(str(show.start_time))
        })
      
      if show.start_time < now:
        past_shows_count += 1
        past_shows.append({
          'venue_id': show.venue_id,
          # 'venue_name': show.venue_name,
          # 'venue_image_link': show.venue_image_link,
          'start_time': format_datetime(str(show.start_time))
        })

  artist_query.upcoming_shows_count = upcoming_shows_count
  artist_query.upcoming_shows = upcoming_shows
  artist_query.past_shows_count = past_shows_count
  artist_query.past_shows = past_shows

  return render_template('pages/show_artist.html', artist=artist_query)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)

  if not artist:
    return redirect(url_for('index'))
  
  form =  ArtistForm(obj=artist)

  genres = [genre  for genre in artist.genres ]
  artist.genres = genres

  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  print(request.form)
  name =  request.form['name']
  city =  request.form['city']
  state =  request.form['state']
  phone =  request.form['phone']
  genres = request.form['genres']
  seeking_venue = True if request.form['seeking_venue'] == 'Yes' else False
  seeking_description = request.form['seeking_description']
  image_link = request.form['image_link']
  website_link = request.form['website_link']
  facebook_link = request.form['facebook_link']
  try:
    artist = Artist.query.get(artist_id)
    artist.name =  name
    artist.city =  city
    artist.state =  state
    artist.phone =  phone
    artist.genre =  genres
    artist.seeking_venue =  seeking_venue
    artist.seeking_description =  seeking_description
    artist.image_link =  image_link
    artist.facebook_link =  facebook_link

    db.session.commit()
  except Exception as err:
    db.session.rollback()
    print('error ', err)
    flash('Error occurred , Could not update Artist ')
    

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
  print('Form data ', request.form)
  name =  request.form['name']
  city =  request.form['city']
  state =  request.form['state']
  phone =  request.form['phone']
  genres = request.form['genres']
  seeking_venue = True if request.form['seeking_venue'] == 'Yes' else False
  seeking_description = request.form['seeking_description']
  image_link = request.form['image_link']
  website_link = request.form['website_link']
  facebook_link = request.form['facebook_link']


  try:
    new_artist = Artist(name=name, city=city, state=state, phone=phone,seeking_venue=seeking_venue, 
    seeking_description=seeking_description,genres=genres, image_link=image_link,website_link=website_link, facebook_link=facebook_link)
    
    db.session.add(new_artist)
    db.session.commit()
    flash('New Artist was saved successfully!')
  except Exception as e:
    print('Error ', e)
    flash('Error saving new Artist')
    redirect(url_for('create_artist_submission'))
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

  



# called upon submitting the new artist listing form
# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion

# on successful db insert, flash success
# flash('Artist ' + request.form['name'] + ' was successfully listed!')
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
# return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
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
  artist_id =  request.form['artist_id']
  venue_id =  request.form['venue_id']
  start_time =  request.form['start_time']

  try:
    new_show = Show(start_time= start_time, venue_id=venue_id, artist_id=artist_id) 
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!', 'success')
  except Exception as err:
    print('Eror ', err)
    db.rollback()
    db.session.close()
    return flash('Error saving a new show!', 'error')
  # on successful db insert, flash success
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
