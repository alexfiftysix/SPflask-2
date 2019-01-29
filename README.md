# SPflask

## Description ##
Band website for Street Pieces using Flask back-end.

## Aim ##
To create a highly-focussed website to showcase music and film clips from the band.
To have a simple user interface for the band to be able to upload their own music, film clips, photos and gig information, hidden from regular users.

## Technologies ##
Flask back end, mySQL (possibly will try Postgres for learning, or back down to MongoDB as the data has no relations)

## Current stage ##
Front-end has been created for desktop. Should work fine on tablets, and mobile.<br>
Back end is now data-driven.

## Future jobs ##
Improve the mobile design for regular users. Allow touch/gesture control.

Use some kind of magic to change the bg-colour dynamically based on the colour of the content (ie. Bandcamp iFrame, youtube player)

Change over to PostgreSQL instead of mySQL for kicks

Improve validation. The website is only intended to have about 4 users with access to the log-in area, but better safe than sorry.

## To Run locally ##
$ export FLASK_APP=app.py <br> 
$ export FLASK_DEBUG=1  // If you want debug mode <br>
$ flask run <br>
