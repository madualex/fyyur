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
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from model import*

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120)) 
    seeking_talent = db.Column(db.String)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref = 'Venue', lazy=True)
    

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
    seeking_venue = db.Column(db.String)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref = 'Artist', lazy=True)


class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  start_time = db.Column(db.DateTime, default=datetime.now)


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
    data = []
    venues = Venue.query.all()
    for venue in venues:
        joined_venue = {
        "city": venue.city,
        "state": venue.state
        }

        displayed_venues = Venue.query.filter_by(city=venue.city, state=venue.state).all()

        list_of_venues = []
        for displayed_venue in displayed_venues:
            upcoming_shows = len(db.session.query(Show).join(Venue).filter(Show.artist_id == Artist.id).filter(Show.start_time > datetime.now()).all())
        
            list_of_venues.append({
                "id": displayed_venue.id,
                "name": displayed_venue.name,
                "num_upcoming_shows": upcoming_shows
        })

        joined_venue["venues"] = list_of_venues
        data.append(joined_venue)
    return render_template('pages/venues.html', areas=data);
@app.route('/venues/search', methods=['POST'])
def search_venues():
    response={}
    search_term = request.form.get("search_term", "")
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    count = len(venues)
    response["data"] = []
    response["count"] = count

    for venue in venues:          
        listed_venues = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(db.session.query(Show).join(Venue).filter(Show.artist_id == Artist.id).filter(Show.start_time > datetime.now()).all())
        }
        response["data"].append(listed_venues)
    
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    data = Venue.query.get(venue_id)
    past_shows = []
    upcoming_shows = []
    listed_shows = {}

    for show in data.show:
        listed_shows['artist_id'] = show.Artist.id
        listed_shows['artist_name'] = show.Artist.name
        listed_shows['artist_image_link'] = show.Artist.image_link
        listed_shows['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M")

        if show.start_time <= datetime.now():
            past_shows.append(listed_shows)
        else:
            upcoming_shows.append(listed_shows)


    setattr(data, "past_shows", past_shows)
    setattr(data, "upcoming_shows", upcoming_shows)
    setattr(data, "past_shows_count", len(past_shows))
    setattr(data, "upcoming_shows_count", len(upcoming_shows))

    print(data)

    return render_template('pages/show_venue.html', venue=data)


# -------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    try:
        new_venue = Venue (
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres= form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
        )

        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was listed successfully!')

    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' was not listed successfully.')
        print(sys.exc_info())

    finally:
        db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE', 'POST'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash("Venue " + venue.name + " has been successfully deleted!")
    except Exception as error:
        print(error)
        db.session.rollback()
        flash("Venue " + venue.name + " could not be deleted!")
    finally:
        db.session.close()
    return render_template('pages/home.html')


# -----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    response={}
    search_term = request.form.get("search_term", "")
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    count = len(artists)
    response['data'] = []
    response['count'] = count


    for artist in artists:          
        listed_artists = {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(db.session.query(Show).join(Venue).filter(Show.artist_id == Artist.id).filter(Show.start_time > datetime.now()).all())
        }
        response['data'].append(listed_artists)

    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    data = Artist.query.get(artist_id)
    past_shows = []
    upcoming_shows = []
    listed_shows = {}

    for show in data.show:
        listed_shows['venue_id'] = show.Venue.id
        listed_shows['venue_name'] = show.Venue.name
        listed_shows['venue_image_link'] = show.Venue.image_link
        listed_shows['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M")


        if show.start_time <= datetime.now():
            past_shows.append(listed_shows)
        else:
            upcoming_shows.append(listed_shows)


    setattr(data, "past_shows", past_shows)
    setattr(data, "upcoming_shows", upcoming_shows)
    setattr(data, "past_shows_count", len(past_shows))
    setattr(data, "upcoming_shows_count", len(upcoming_shows))

    
    print(data)
    return render_template('pages/show_artist.html', artist=data)


# -----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)

    if form.validate:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data  
        artist.phone = form.phone.data
        artist.genres = form.genres.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website_link = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data  

        try:
            db.session.add(artist)
            db.session.commit()
            flash("Artist " + artist.name + " was successfully edited!")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash("An error has occured!")
        finally:
            db.session.close()
    else:
            flash("An error occured. Try again.")

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)

    if form.validate:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data  
        venue.phone = form.phone.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website_link = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data  

        try:
            db.session.add(venue)
            db.session.commit()
            flash("Venue " + venue.name + " was edited successfully!")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash("Venue editing encountered an error.")
        finally:
            db.session.close()
    else:
            flash("Venue editing not successful.")

    return redirect(url_for('show_venue', venue_id=venue_id))


# -----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    try:
        new_artist = Artist (
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres= form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
        )

        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was listed successfully!')

    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' was not listed.')
        print(sys.exc_info())

    finally:
        db.session.close()
    return render_template('pages/home.html')

# -----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data=[]
  for show in shows:
    data.append({
          "venue_id": show.Venue.id,
          "venue_name": show.Venue.name,
          "artist_id": show.Artist.id,
          "artist_name": show.Artist.name,
          "artist_image_link": show.Artist.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)
  

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    post_show = Show(
          artist_id = form.Artist_id.data,
          venue_id = form.Venue_id.data,
          start_time = form.start_time.data
      )
    try:
        db.session.add(post_show)
        db.session.commit()
        flash('Show posted successfully!')

    except Exception:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Try posting show again!')

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
