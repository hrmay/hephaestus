#------------------------------------
# SERVER.PY
# Python file for all of the app
# routes and algorithms and such.
#------------------------------------

import os
from flask import Flask, render_template, request, redirect, url_for, session
import random
import psycopg2
import psycopg2.extras

app = Flask(__name__)

app.secret_key = os.urandom(24).encode('hex')

def formatDate(date):
    #Get those months
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
    
    splitDate = str(date).split("-");
    newDate = months[int(splitDate[1])-1];
    newDate += " " + str(splitDate[2]);
    newDate += ", " + str(splitDate[0]);
    
    return newDate;
    
def connectToDB():
    connectionString = 'dbname=hephaestus user=heph password=4SrGY9gPFU72aJxh host=localhost'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Can't connect to database.")

@app.route('/')
def mainIndex():
    worldid = '1'
    world_results = worldinfo(worldid)
    description = worlddesc(worldid)
    return render_template("index.html", world=world_results, world_desc = description[0][1], worldID = worldid);
    
@app.route('/article')
def articletest():
     return render_template("article.html");

#------------------------------------
#  World Routes
#------------------------------------

#Grabs info for world to be displayed on sidebar of worlds and articles     
def worldinfo(worldid):
    conn = connectToDB()
    cur = conn.cursor()
    
    query = {'worldid': worldid}
    
    #grab world info
    try:
        cur.execute("""SELECT world.Name, member.Username, COUNT(DISTINCT category.CategoryID), COUNT(DISTINCT article.ArticleID), genre.Genre FROM world JOIN member ON (world.CreatorID = member.UserID) JOIN category ON (world.WorldID = category.WorldID) JOIN article ON (world.WorldID = article.WorldID) JOIN genre ON (world.WorldID = genre.WorldID) WHERE world.WorldID = %(worldid)s AND genre.PrimaryGenre = True GROUP BY world.Name, member.Username, genre.Genre;""", query)
    except:
        print("ERROR executing SELECT")
        print(cur.mogrify("""SELECT world.Name, member.Username, COUNT(DISTINCT category.CategoryID), COUNT(DISTINCT article.ArticleID) FROM world JOIN member ON (world.CreatorID = member.UserID) JOIN category ON (world.WorldID = category.WorldID) JOIN article ON (world.WorldID = article.WorldID) WHERE world.WorldID = %(worldid)s AND genre.PrimaryGenre = True GROUP BY world.Name, member.Username, genre.Genre;""", query))
    world_results = cur.fetchall()
    
    #grab category names
    try:
        cur.execute("""SELECT category.Name, article.Name FROM category JOIN world ON (category.WorldID = world.WorldID) JOIN article ON (category.CategoryID = article.CategoryID) WHERE world.WorldID = %(worldid)s ORDER BY category.Name, article.Name;""", query)
    except:
        print("ERROR executing SELECT")
        print(cur.mogrify("""SELECT category.Name, article.Name FROM category JOIN world ON (category.WorldID = world.WorldID) JOIN article ON (category.CategoryID = article.CategoryID) WHERE world.WorldID = %(worldid)s ORDER BY category.Name, article.Name;""", query))
    category_results = cur.fetchall()
    
    ca_results = {}
    for category in category_results:
        if category[0] in ca_results:
            ca_results[category[0]].append(category[1])
        else:
            ca_results[category[0]] = [category[1]]

    results = [world_results, ca_results];
    return results

#Grabs the description of a world    
def worlddesc(worldid):
    conn = connectToDB()
    cur = conn.cursor()
    
    query = {'worldid': worldid}
    
    try:
        cur.execute("""SELECT LongDesc, ShortDesc FROM world WHERE WorldID = %(worldid)s;""", query)
    except:
        print("ERROR executing SELECT")
    
    description = cur.fetchall();
    return description

@app.route('/world/<worldid>')
def world(worldid):
    results = worldinfo(worldid)
    
    description = worlddesc(worldid)
    
    return render_template("world.html", world_info = results, world_description=description[0][0], color="#aaaaaa");

#------------------------------------
#  End World
#------------------------------------


#------------------------------------
#  Article Routes
#------------------------------------

#Grabs information to display an article
def articledesc(worldid, categoryname, articlename):
    conn = connectToDB()
    cur = conn.cursor()
    
    #holds all of the query information; SELECT doesn't work without it
    query = {'world': worldid, 'category': categoryname, 'article':articlename}
    
    try:
        cur.execute("""SELECT article.Name, article.Body FROM article JOIN category ON (article.CategoryID = category.CategoryID) JOIN world ON (article.WorldID = world.WorldID) WHERE world.WorldID = %(world)s AND category.Name = %(category)s AND article.Name = %(article)s;""", query)
    except:
        print("ERROR executing SELECT")
        print(cur.mogrify("""SELECT article.Name, article.Body FROM article JOIN category ON (article.CategoryID = category.CategoryID) JOIN world ON (article.WorldID = world.WorldID) WHERE world.WorldID = %(world)s AND category.Name = %(category)s AND article.Name = %(article)s;""", query))

    description = cur.fetchall()
    
    return description

@app.route('/world/<worldid>/<categoryname>/<articlename>')
def article(worldid, categoryname, articlename):
    world_results = worldinfo(worldid)
    article_results = articledesc(worldid, categoryname, articlename)
    
    return render_template("article.html", world_info = world_results, article_description = article_results, color="#aaaaaa");

#------------------------------------
#  End Article
#------------------------------------

#------------------------------------
#  User Routes
#------------------------------------
    
@app.route('/user/<username>', methods=['GET'])
def user(username):
    #Database connection
    conn = connectToDB()
    cur = conn.cursor()
    
    if request.method == 'GET':
        #Get the user info for their page
        try:
            cur.execute("""SELECT username, joindate, (SELECT email FROM member WHERE dispemail IS True AND LOWER(username) = LOWER('%s')) email FROM member WHERE LOWER(username) = LOWER('%s');""" %(username, username))
            results = cur.fetchall()
            results = list(results[0]);
            results[1] = formatDate(results[1]);
        except:
            print("Failed to execute the following: ")
            print(cur.mogrify("""SELECT username, joindate, (SELECT email FROM member WHERE dispemail IS True AND LOWER(username) = LOWER('%s')) email FROM member WHERE LOWER(username) = LOWER('%s');""" %(username, username)))
            results = None;
        
        #Get user's created worlds
        try:
            query = {'username':username}
            cur.execute("""SELECT world.WorldID FROM world JOIN member ON (world.CreatorID = member.UserID) WHERE LOWER(member.Username) = LOWER(%(username)s);""", query);
            worldid_results = cur.fetchall()
            print(worldid_results[0])
        except:
            print("ERROR executing SELECT")
            print(cur.mogrify("""SELECT world.WorldID FROM world JOIN member ON (world.CreatorID = member.UserID) WHERE LOWER(member.Username) = LOWER(%(username)s);""", query))

        worlds = []
        if len(worldid_results) > 0:
            worldid_results = worldid_results[0];
            print(worldid_results)
            for worldid in worldid_results:
                print(worldid)
                worldname = worldinfo(worldid)[0][0][0]
                worlddescription = worlddesc(worldid)[0][0]
                world = [worldname, worlddescription]
                worlds.append(world)
                print(worlds)

        #Get user's collaborative worlds
        try:
            query = {'username':username}
            cur.execute("""SELECT world.WorldID FROM world JOIN userworlds ON (world.WorldID = userworlds.UserID) JOIN member ON (userworlds.UserID = member.UserID) WHERE LOWER(member.Username) = LOWER(%(username)s) AND userworlds.Role = 'Editor';""", query);
            worldid_results = cur.fetchall()
            print(worldid_results[0])
        except:
            print("ERROR executing SELECT")
            print(cur.mogrify("""SELECT world.WorldID FROM world JOIN member ON (world.CreatorID = member.UserID) WHERE LOWER(member.Username) = LOWER(%(username)s);""", query))

        collab_worlds = []
        if len(worldid_results) > 0:
            worldid_results = worldid_results[0];
            print(worldid_results)
            for worldid in worldid_results:
                print(worldid)
                worldname = worldinfo(worldid)[0][0][0]
                worlddescription = worlddesc(worldid)[0][0]
                world = [worldname, worlddescription]
                worlds.append(world)
                print(worlds)
        
        
        
        color="#aaaaaa";
    
    return render_template("user.html", user_info = results, color=color, worlds=worlds);

#------------------------------------
#  End User
#------------------------------------


#------------------------------------
#  Signup Routes
#------------------------------------
@app.route('/signup')
def signup():
    return render_template('signup.html', errors=None)

@app.route('/signup1', methods=['POST'])
def signup1():
    #Database connection
    conn = connectToDB()
    cur = conn.cursor()
    query = {
        'username'         : request.form['username'],
        'email'            : request.form['email'],
        'password'         : request.form['password'],
        'confirm_password' : request.form['confirm_password']
    }
    
    try:
        #Check that no one has this username or this email
        cur.execute("""SELECT username, email FROM member WHERE LOWER(username) = LOWER(%(username)s) OR LOWER(email) = LOWER(%(email)s);""", query)
        print(cur.mogrify("""SELECT username, email FROM member WHERE LOWER(username) = LOWER(%(username)s) OR LOWER(email) = LOWER(%(email)s);""", query))
        results = cur.fetchall()
    except:
        print("Failed to execute the following: ")
        print(cur.mogrify("""SELECT username, email FROM member WHERE LOWER(username) = LOWER(%(username)s) OR LOWER(email) = LOWER(%(email)s);""", query))
        
    #Check
    u_free = True;
    e_free = True;
    
    if len(results) >= 1:
        for result in results:
            if result[0].lower() == query['username'].lower():
                u_free = False;
            if result[1].lower() == query['email'].lower():
                e_free = False;
        
    #Check that passwords match
    p_match = (query['password'] == query['confirm_password'])
    all_okay = (p_match and u_free and e_free)
    
    if (request.method == 'POST' and all_okay == True):
        try:
            cur.execute("""INSERT INTO member (username, email, password, joindate) VALUES (%(username)s, %(email)s, crypt(%(password)s, gen_salt('bf')), now());""", query)
        except:
            print("Failed to execute the following: ")
            print(cur.mogrify("""INSERT INTO member (username, email, password, joindate) VALUES (%(username)s, %(email)s, crypt(%(password)s, gen_salt('bf')), now());""", query))
            conn.rollback()
            return render_template("signup.html", errors = None) #Fix this later to give a message
    else:
        return render_template("signup.html", errors = [u_free, e_free, p_match]);
        
    conn.commit()    
    
    return redirect(url_for('mainIndex'))
    
#------------------------------------
#  End Signup
#------------------------------------

#------------------------------------
#  Login Route
#------------------------------------

@app.route('/login', methods=['GET'])
def login():
    #Database connection
    conn = connectToDB()
    cur = conn.cursor()
    query = {
        'username' : request.form['username_login'],
        'password' : request.form['password_login'],
    }
    rule = request.url_rule #Get the page to redirect to if login succeeds
    print('Rule: ' + rule)
    
    if (request.method == 'GET'):
        try:
            cur.execute("""SELECT * FROM member WHERE lower(member.username) = lower(%(username)s)""", query)
        except:
            print(cur.mogrify("""SELECT * FROM member WHERE lower(member.username) = lower(%(username)s)""", query))
            return render_template("login.html")
    else:
        return redirect()
        
    return redirect(url_for(rule));
    
#------------------------------------
#  End Login
#------------------------------------

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug = True)