Hephaestus <img src="https://i.gyazo.com/2947ce425f238815fff8617065b1a780.png" width=32 height=32>
===========================================

A (draft of a) web application for creating fantasy worlds for novels, games, etc. Once they've created an account,
users can create worlds, work with collaborators (or alone!), and share their public files with any viewers. 

Note, all of the sensitive data in this repo is completely visible. It wasn't necessary that we keep it private, given
that it was only a class assignment that was developed locally, but in the event that you use this code for something serious,
make sure to hide sensitive data with the <code>.gitignore</code> and ensure that it's not publicly visible in C9 (either
create a private workspace for it, or hide it outside of the workspace directory).

Setup
-----

After downloading the respository on your server, you'll need to install Flask, its SocketIO package, and psycopg2. The following commands should install all dependencies for Cloud9 users:


    #To install Flask:
    sudo easy_install Flask
    #To install Flask-SocketIO:
    sudo easy_install flask-socketio
    #To install psycopg2: 
    sudo apt-get install python-psycopg2
    
This application uses a Postgres database. For Cloud9 users, the following should setup your database:


    sudo apt-get install postgresql-contrib-9.3
    #Start postgresql and create a new password for the default use (postgres)
    service postgresql start
    sudo sudo -u postgres psql
    /password
    #Create your new password here
    #Log into the postgres account with your new password
    psql -U postgres -h localhost
    \i heph.sql #Run this file to create the database, tables, roles, and test data

Lastly, log out of Postgres and run the server.py file to begin running the application.
