#------------------------------------
# SERVER.PY
# Python file for all of the app
# routes and algorithms and such.
#------------------------------------

import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask.ext.socketio import SocketIO, emit
import random
import psycopg2
import psycopg2.extras
import time

app = Flask(__name__)

app.secret_key = os.urandom(24).encode('hex')

socketio = SocketIO(app)

usersOnline = {}

#----------------------
# FORMAT DATE
#----------------------
def formatDate(date):
    #Get those months
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
    
    splitDate = str(date).split("-");
    newDate = months[int(splitDate[1])-1];
    newDate += " " + str(splitDate[2]);
    newDate += ", " + str(splitDate[0]);
    
    return newDate;
#end formatDate()  
    
#----------------------
# GET USER INFO
#----------------------
def getUser():
    currentUser = {}
    if 'username' in session:
        currentUser['username'] = session['username']
    else:
        currentUser['username'] = ''
    return currentUser
#end getUser()
    
#----------------------
# CONNECT TO DB
#----------------------
def connectToDB():
    connectionString = 'dbname=hephaestus user=hermes password=4SrGY9gPFU72aJxh host=localhost'
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Can't connect to database.")
#end connectToDB()

#----------------------
# WORLD INFO
#----------------------
#Grabs info for world to be displayed on sidebar of worlds and articles     
def worldinfo(worldid):
    conn = connectToDB()
    cur = conn.cursor()
    world_results = []
    category_results = []
    
    query = {'worldid': worldid}
    print(worldid)
    
    #grab world info
    try:
        cur.execute("SELECT world.Name, member.Username, world.PrimGenre FROM world JOIN member ON (world.CreatorID = member.UserID) WHERE world.WorldID = %(worldid)s;", query)
        world_results = cur.fetchall()
    except:
        print("ERROR executing SELECT")
        print(cur.mogrify("SELECT world.Name, member.Username, world.PrimGenre FROM world JOIN member ON (world.CreatorID = member.UserID) WHERE world.WorldID = %(worldid)s;", query))
        world_results = None
        
    raw_categories = []
    #grab raw categories
    try:
        cur.execute("SELECT category.Name FROM category JOIN world ON (category.WorldID = world.WorldID) WHERE world.WorldID = %(worldid)s ORDER BY LOWER(category.Name);", query)
    except:
        print("Failed to execute: "),
        print(cur.mogrify("SELECT category.Name FROM category JOIN world ON (category.WorldID = world.WorldID) WHERE world.WorldID = %(worldid)s ORDER BY LOWER(category.Name);", query))
    
    #insert all the categories into the dictionary
    ca_results = {}
    if cur.rowcount > 0:
        raw_categories = cur.fetchall()
        for raw_category in raw_categories:
            ca_results[raw_category[0]] = []
    
    #grab category names and articles
    try:
        cur.execute("""SELECT category.Name, article.Name FROM category JOIN world ON (category.WorldID = world.WorldID) JOIN article ON (category.CategoryID = article.CategoryID) WHERE world.WorldID = %(worldid)s ORDER BY LOWER(category.Name), LOWER(article.Name);""", query)
    except:
        print("ERROR executing SELECT")
        print(cur.mogrify("""SELECT category.Name, article.Name FROM category JOIN world ON (category.WorldID = world.WorldID) JOIN article ON (category.CategoryID = article.CategoryID) WHERE world.WorldID = %(worldid)s ORDER BY LOWER(category.Name), LOWER(article.Name);""", query))
    
    category_article_counts = [] #[0] is category count, [1] is article count
    
    #insert all the articles under their corresponding categories
    if cur.rowcount > 0:
        category_results = cur.fetchall()
        tempCategories = [x[0] for x in category_results]
        category_article_counts.append(len(set(raw_categories))) #category count
        category_article_counts.append(len(category_results)) #article count
        for category in category_results:
            if category[0] in ca_results:
                ca_results[category[0]].append(category[1])
            else:
                ca_results[category[0]] = [category[1]]
    else:
        category_article_counts = [len(set(raw_categories)),0]
    print(ca_results)

    results = [world_results, ca_results, category_article_counts];
        
    return results
#end worldinfo()

#----------------------
# WORLD DESCRIPTION
#----------------------
#Grabs the description of a world    
def worlddesc(worldid):
    conn = connectToDB()
    cur = conn.cursor()
    
    query = {'worldid': worldid}
    
    try:
        cur.execute("""SELECT LongDesc, ShortDesc FROM world WHERE WorldID = %(worldid)s;""", query)
        description = cur.fetchall();
    except:
        print("ERROR executing SELECT")
        description = None
    
    
    return description
#end worlddesc()

#----------------------
# ARTICLE DESCRIPTION
#----------------------
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
#end articledesc

#------------------------------------
#  PERMISSIONS
#------------------------------------
def getPermissions(worldid):
    if 'username' in session:
        conn = connectToDB()
        cur = conn.cursor()
        query = {'username': session['username'], 'worldid': worldid}
        try:
            cur.execute("SELECT member.Username FROM member JOIN world ON (world.CreatorID = member.UserID) JOIN userworlds ON (userworlds.UserID = member.UserID) WHERE world.CreatorID = (SELECT UserID FROM member WHERE Username = %(username)s) OR (userworlds.WorldID = %(worldid)s AND userworlds.UserID IN (SELECT UserID FROM member WHERE Username = %(username)s) AND userworlds.Role = 'Editor');", query)
        except:
            print("Failed to execute: "),
            print(cur.mogrify("SELECT member.Username FROM member JOIN world ON (world.CreatorID = member.UserID) JOIN userworlds ON (userworlds.UserID = member.UserID) WHERE world.CreatorID = (SELECT UserID FROM member WHERE Username = %(username)s) OR (userworlds.WorldID = %(worldid)s AND userworlds.UserID IN (SELECT UserID FROM member WHERE Username = %(username)s) AND userworlds.Role = 'Editor');", query))
        if cur.rowcount > 0:
            #they have permissions
            return True
    else:
        return False #can't have permissions if you're not logged in

#------------------------------------
#  SOCKET IO
#------------------------------------
@socketio.on('connect', namespace='/heph')
def makeConnection():
    session['uuid'] = uuid.uuid1()
    print('connected')
    print(usersOnline)
    for user in usersOnline:
        print(user)
        emit('users', usersOnline[user])
        
@socketio.on('users', namespace='/heph')
def updateUsers(location):
    tempUser = {'username': session['username'], 'location':location, 'time': time.time()}
    usersOnline[session['username']] = tempUser
    emit('users', tempUser, broadcast=True)
    
@socketio.on('newUser', namespace='/heph')
def newUser(location):
    tempUser = {'username': session['username'], 'location':location, 'time': time.time()}
    if session['username'] in usersOnline:
        del usersOnline[session['username']]
        usersOnline[session['username']] = tempUser
        emit('replaceUser', tempUser, broadcast=True)
    else:
        usersOnline[session['username']] = tempUser
        emit('newUser', tempUser, broadcast = True)

#------------------------------------
#  MAIN ROUTES
#------------------------------------
@app.route('/')
def mainIndex():
    worldid = '1'
    world_results = worldinfo(worldid)
    description = worlddesc(worldid)
    return render_template("index.html", world=world_results, world_desc = description[0][1], worldID = worldid, user=getUser());
#end mainIndex()    

#------------------------------------
#  WORLD ROUTES
#------------------------------------
@app.route('/world/<worldid>')
def world(worldid):
    results = worldinfo(worldid)
    print(worldid)
    description = worlddesc(worldid)
    
    return render_template("world.html", world_info = results, world_description=description, worldid = worldid, color="#aaaaaa", user=getUser(), viewing_world = True, permissions=getPermissions(worldid));

#------------------------------------
#  End World
#------------------------------------


#------------------------------------
#  Article Routes
#------------------------------------

@app.route('/world/<worldid>/<categoryname>/<articlename>')
def article(worldid, categoryname, articlename):
    world_results = worldinfo(worldid)
    article_results = articledesc(worldid, categoryname, articlename)
    print(article_results)
    
    return render_template("article.html", world_info = world_results, article_description = article_results, worldid = worldid, color="#aaaaaa", user=getUser(), viewing_world=False, permissions=getPermissions(worldid));

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
            cur.execute("""SELECT username, joindate, (SELECT email FROM member WHERE dispemail IS True AND LOWER(username) = LOWER('%s')) email, userdesc FROM member WHERE LOWER(username) = LOWER('%s');""" %(username, username))
            results = cur.fetchall()
            results = list(results[0]);
            results[1] = formatDate(results[1]);
        except:
            print("Failed to execute: "),
            print(cur.mogrify("""SELECT username, joindate, (SELECT email FROM member WHERE dispemail IS True AND LOWER(username) = LOWER('%s')) email, userdesc FROM member WHERE LOWER(username) = LOWER('%s');""" %(username, username)))
            results = None;
        
        #Get user's created worlds
        try:
            query = {'username':username}
            cur.execute("""SELECT world.WorldID FROM world JOIN member ON (world.CreatorID = member.UserID) WHERE LOWER(member.Username) = LOWER(%(username)s);""", query);
            worldid_results = cur.fetchall()
            print(worldid_results[0])
        except:
            print("Failed to execute: ")
            print(cur.mogrify("""SELECT world.WorldID FROM world JOIN member ON (world.CreatorID = member.UserID) WHERE LOWER(member.Username) = LOWER(%(username)s);""", query))

        #put the created worlds into an array
        worlds = []
        if len(worldid_results) > 0:
            for worldid in worldid_results:
                tempID = worldid[0]
                print(worldinfo(tempID))
                worldname = worldinfo(tempID)[0][0][0]
                worlddescription = worlddesc(tempID)[0][1]
                world = [tempID, worldname, worlddescription]
                worlds.append(world)

        #Get user's collaborative worlds
        try:
            query = {'username':username}
            cur.execute("""SELECT userworlds.WorldID FROM userworlds JOIN member ON (userworlds.userid = member.UserID) WHERE LOWER(member.Username) = LOWER(%(username)s);""", query)
            collab_results = cur.fetchall()
        except:
            print("ERROR executing SELECT")
            print(cur.mogrify("""SELECT userworlds.WorldID FROM userworlds JOIN member ON (userworlds.userID = member.UserID) WHERE LOWER(member.Username) = LOWER(%(username)s);""", query))

        #put collab worlds into an array
        collabs = []
        if len(collab_results) > 0:
            collab_results = collab_results[0];
            for collabid in collab_results:
                colname = worldinfo(collabid)[0][0][0]
                coldescription = worlddesc(collabid)[0][1]
                collab = [collabid, colname, coldescription]
                collabs.append(collab)
        
        color="#aaaaaa";
    
    return render_template("user.html", user_info = results, color=color, worlds=worlds, collabs=collabs, user=getUser());

#------------------------------------
#  End User
#------------------------------------


#------------------------------------
#  Signup Routes
#------------------------------------
@app.route('/signup', methods=['POST','GET'])
def signup():
    if 'username' in session:
        #flash("You're already signed up! (And logged in...?)", 'session_error')
        return redirect(url_for('mainIndex'))
    
    errorList = []
    if request.method == 'GET':
        return render_template('signup.html', errors=errorList, user=getUser())
    elif request.method == 'POST':
        #Database connection
        conn = connectToDB()
        cur = conn.cursor()
        
        query = {
            'username'         : request.form['username'],
            'email'            : request.form['email'],
            'password'         : request.form['password'],
            'confirm_password' : request.form['confirm_password']
        }
        
        try: #Check that no one has this username or this email
            cur.execute("""SELECT username, email FROM member WHERE LOWER(username) = LOWER(%(username)s) OR LOWER(email) = LOWER(%(email)s);""", query)
            results = cur.fetchall()
        except:
            print("Failed to execute: "),
            print(cur.mogrify("""SELECT username, email FROM member WHERE LOWER(username) = LOWER(%(username)s) OR LOWER(email) = LOWER(%(email)s);""", query))
            
            errorList.append({'type':'database','message':'Failed to check the database! Please report this error.'})
            return render_template("signup.html", errors = errorList, user=getUser())
            
        #Check
        u_free = True;
        e_free = True;
        
        if len(results) >= 1:
            for result in results:
                if result[0].lower() == query['username'].lower():
                    u_free = False;
                    errorList.append({'type':'username','message':'This username already exists!'})
                if result[1].lower() == query['email'].lower():
                    e_free = False;
                    errorList.append({'type':'email','message':'This email already exists!'})
            
        #Check that passwords match
        p_match = (query['password'] == query['confirm_password'])
        if p_match == False:
            errorList.append({'type':'password','message':'Your passwords did not match!'})
        all_okay = (p_match and u_free and e_free)
        
        if (request.method == 'POST' and all_okay == True):
            try:
                cur.execute("""INSERT INTO member (username, email, password, joindate) VALUES (%(username)s, %(email)s, crypt(%(password)s, gen_salt('bf')), now());""", query)
                session['username'] = query['username']
            except:
                print("Failed to execute: "),
                print(cur.mogrify("""INSERT INTO member (username, email, password, joindate) VALUES (%(username)s, %(email)s, crypt(%(password)s, gen_salt('bf')), now());""", query))
                conn.rollback()
                
                errorList.append({'type':'database','message':'Failed to add you to the database! Please report this error.'})
                return render_template("signup.html", errors = errorList, user=getUser())
        else:
            return render_template("signup.html", errors = errorList, user=getUser())
            
        conn.commit()    
        return redirect(url_for('mainIndex'))
    
#------------------------------------
#  End Signup
#------------------------------------

#------------------------------------
#  Login Route
#------------------------------------

@app.route('/login', methods=['POST','GET'])
def login():
    if 'username' in session:
        flash('You''re already logged in!', 'session_error')
        return redirect(url_for('login'))
    
    errorList = []
    if (request.method == 'GET'):
        return render_template("login.html", errors = errorList, user=getUser())
    elif (request.method == 'POST'):
        #Database connection
        conn = connectToDB()
        cur = conn.cursor()
        
        query = {
            'username' : request.form['username_login'],
            'password' : request.form['password_login'],
            'redirect' : request.form['login_redirect']
        }
        
        try:
            cur.execute("""SELECT member.username FROM member WHERE lower(member.username) = lower(%(username)s) AND member.Password = crypt(%(password)s, member.Password)""", query)
            if cur.rowcount == 1:
                name = cur.fetchone()
                session['username'] = name[0]
            else:
                print("No user found with that username and password.")
                errorList.append({'type':'username', 'message':'Your username or password was incorrect! Please try logging in again.'})
                return render_template("login.html", errors = errorList, user=getUser(), loginRedirect=query['redirect']) 
        except:
            print('Failed to execute: '),
            print(cur.mogrify("""SELECT * FROM member WHERE lower(member.username) = lower(%(username)s) AND member.Password = crypt(%(password)s, member.Password)""", query))
            errorList.append({'type':'database','message':'Failed to check the database! Please report this error.'})
            return render_template("login.html", errors = errorList, user=getUser(), loginRedirect=query['redirect'])
    else:
        return redirect(query['redirect'])
    
    return redirect(query['redirect'])
    
#------------------------------------
#  End Login
#------------------------------------


#------------------------------------
#  Logout
#------------------------------------

@app.route('/logout')
def logout():
    del usersOnline[session['username']]
    socketio.emit('deleteUser', session['username'])
    session.pop('username', None)
    return redirect(url_for('mainIndex'))

#------------------------------------
#  End Logout
#------------------------------------

#------------------------------------
#  CREATION ROUTES
#------------------------------------
@app.route('/createworld', methods=['POST','GET'])
def createworld():
    #Redirect users who aren't logged in
    if 'username' not in session:
        flash('Please login before accessing this page!', 'session_error')
        return redirect(url_for('login'))
    
    success = False
    worldid = -1
    #For connecting to the database
    conn = connectToDB()
    cur = conn.cursor()
    
    #Select the primary genres options
    try:
        cur.execute("""SELECT enum_range(NULL::prim_genre);""");
    except:
        print("Failed to execute: "),
        print(cur.mogrify("""SELECT enum_range(NULL::prim_genre);"""))
        flash('Failed to check the database! Please report this error.', 'database_error')
        
    #Get genres and sort alphabetically
    genres = cur.fetchone()[0].split(',')
    genres = [genre.replace('"','').replace('{','').replace('}','') for genre in genres] #Remove unnecessary characters
    genres = sorted(genres)
    
    if request.method == 'GET':
        return render_template('create_world.html', user=getUser(), genres=genres)
        
    elif request.method == 'POST':
        #Get information from the form
        privacy = request.form['privacy']
        private = False
        if (privacy == 'private'):
            private = True
        
        newWorld = {
            'creator'       : session['username'],
            'name'          : request.form['world-name'],
            'prim-genre'    : request.form['primary-genre'],
            'private'       : private,
            'short-desc'    : request.form['short-desc'],
            'collab_list'   : [name.strip() for name in request.form['collab-details'].split(',')]
        }
        print('Adding a new world: '),
        print(newWorld)
        
        #Check
        #1. That they don't already have a world with this name
        #2. ?????
        
        try:
            #Add the world and get its ID
            cur.execute("""INSERT INTO world (creatorid, name, primgenre, private, shortdesc) VALUES ((SELECT userid FROM member WHERE member.username = %(creator)s), %(name)s, %(prim-genre)s, %(private)s, %(short-desc)s);""", newWorld)
            cur.execute("""SELECT worldid FROM world WHERE world.name = %(name)s and world.creatorid = (SELECT userid FROM member WHERE member.username = %(creator)s);""", newWorld)
            worldid = cur.fetchone()[0]
            
            #Add any collaborators
            if (privacy == 'collab'):
                for name in newWorld['collab_list']:
                    try:
                        cur.execute("""INSERT INTO UserWorlds(WorldID, UserID) VALUES(%(worldid)s,((SELECT userid FROM member WHERE LOWER(member.username) = LOWER(%(name)s))));""", {'worldid':worldid,'name':name})
                    except:
                        print(cur.mogrify("""INSERT INTO UserWorlds(WorldID, UserID) VALUES(%(worldid)s,((SELECT userid FROM member WHERE LOWER(member.username) = LOWER(%(name)s))));""", {'worldid':worldid,'name':name}))
                        flash('Failed to add user ' + name + '! Please double-check this username and try again.', 'creation_error')
                        conn.rollback()
                        
                        return render_template('create_world.html', user=getUser(), genres=genres)
            
            #World (and any collaborators) added successfully!
            success = True
        except:
            print("Failed to execute: "),
            print(cur.mogrify("""INSERT INTO world (creatorid, name, primgenre, private, shortdesc) VALUES ((SELECT userid FROM member WHERE member.username = %(creator)s), %(name)s, %(prim-genre)s, %(private)s, %(short-desc)s);""", newWorld))
            flash('Failed to reach the database! Please report this error.', 'database_error')
            conn.rollback()
            
        conn.commit()
        
    #If successful, redirect!
    if (success):
        return redirect(url_for('world', worldid=worldid))
    #If not, redirect back to the page with any errors added
    else:
        flash('There was a problem creating this world! Please try again.', 'creation_error')
        return render_template('create_world.html', user=getUser(), genres=genres)
# end createworld

        
@app.route('/world/<worldid>/newcategory', methods=['GET', 'POST'])
def newCategory(worldid):
    #you have to be logged in to do this
    if 'username' not in session:
        flash('Please login before accessing this page!', 'session_error')
        return redirect(url_for('login'))
    
    
    #connect to the database
    conn = connectToDB()
    cur = conn.cursor()
    
    query = {'worldid': worldid, 'username': session['username']}
    
    #get permissions
    try:
        cur.execute("""SELECT member.Username FROM member JOIN world ON world.creatorid = member.userid JOIN userworlds ON userworlds.userid = member.userid WHERE world.worldid = %(worldid)s OR userworlds.worldid = %(worldid)s AND member.username=%(username)s;""", query)
    except:
        print("Failed to execute: "),
        print(cur.mogrify("""SELECT member.Username FROM member JOIN world ON world.creatorid = member.userid JOIN userworlds ON userworlds.userid = member.userid WHERE world.worldid = %(worldid)s OR userworlds.worldid = %(worldid)s AND member.username=%(username)s;""", query))
    
    
    if cur.rowcount != 1:
        #you're not the real creator
        flash('You don''t have the permission to do that!', 'permission_error')
        return redirect(url_for('mainIndex'))
    else:
        if request.method == 'GET':
            return render_template('new_category.html', user=getUser(), worldid=worldid)
        elif request.method == 'POST':
            cat_query = {'worldid': worldid, 'catname': request.form['category-name']}
            try:
                cur.execute("SELECT category.Name FROM category WHERE category.WorldID = %(worldid)s AND category.Name = %(catname)s;", cat_query)
                if cur.rowcount < 1:
                    try:
                        cur.execute("""INSERT INTO category (WorldID, Name) VALUES(%(worldid)s, %(catname)s);""", cat_query)
                    except:
                        print("Failed to execute: "),
                        print(cur.mogrify("""INSERT INTO category (WorldID, Name) VALUES(%(worldid)s, %(catname)s);""", cat_query))
                        conn.rollback()
                    conn.commit()
                else:
                    #a category with this name already exists
                    #add error message
                    return redirect(url_for('world', worldid=worldid))
            except:
                print("Failed to execute: "),
                print(cur.mogrify("SELECT category.Name FROM category WHERE category.WorldID = %(worldid)s AND category.Name = %(catname)s;", cat_query))
                
        return redirect(url_for('world', worldid=worldid))
# end newcategory

@app.route('/world/<worldid>/<category>/newarticle', methods=['GET', 'POST'])
def newArticle(worldid, category):
    #you have to be logged in to do this
    if 'username' not in session:
        flash('Please login before accessing this page!', 'session_error')
        return redirect(url_for('login'))
    
    
    #connect to the database
    conn = connectToDB()
    cur = conn.cursor()
    
    query = {'worldid': worldid, 'category': category, 'username': session['username']}
    
    #get permissions
    try:
        cur.execute("""SELECT member.Username FROM member JOIN world ON world.creatorid = member.userid JOIN userworlds ON userworlds.userid = member.userid WHERE world.worldid = %(worldid)s OR userworlds.worldid = %(worldid)s AND member.username=%(username)s;""", query)
    except:
        print("Failed to execute: "),
        print(cur.mogrify("""SELECT member.Username FROM member JOIN world ON world.creatorid = member.userid JOIN userworlds ON userworlds.userid = member.userid WHERE world.worldid = %(worldid)s OR userworlds.worldid = %(worldid)s AND member.username=%(username)s;""", query))
    
    if cur.rowcount < 1:
        #you're not in the permissions
        print('User does not have permission to complete this action')
        flash('You don''t have the permission to do that!', 'permission_error')
        return redirect(url_for('mainIndex'))
    else:
        if request.method == 'GET':
            return render_template('new_article.html', user=getUser(), worldid=worldid, category=category)
        elif request.method == 'POST':
            article_query = {'worldid': worldid, 'category':category, 'articlename': request.form['article-name'], 'articlebody': request.form['article-body']}
            try:
                cur.execute("""SELECT article.Name FROM article WHERE article.CategoryID = (SELECT CategoryID FROM category WHERE Name = %(category)s) AND article.Name = %(articlename)s;""", article_query)
                if cur.rowcount < 1:
                    try:
                        cur.execute("""INSERT INTO article (WorldID, CategoryID, Name, Body) VALUES(%(worldid)s, (SELECT CategoryID FROM category WHERE Name = %(category)s), %(articlename)s, %(articlebody)s);""", article_query)
                    except:
                        print("Failed to execute: "),
                        print(cur.mogrify("""INSERT INTO article (WorldID, CategoryID, Name, Body) VALUES(%(worldid)s, (SELECT CategoryID FROM category WHERE Name = %(category)s), %(articlename)s, %(articlebody)s);""", article_query))
                        conn.rollback()
                    conn.commit()
                else:
                    #an article with this name already exists
                    #add error message
                    return redirect(url_for('world', worldid=worldid))
            except:
                print("Failed to execute: "),
                print(cur.mogrify("""SELECT article.Name FROM article WHERE article.CategoryID = (SELECT CategoryID FROM category WHERE Name = %(category)s) AND article.Name = %(articlename)s;""", article_query))
        return redirect(url_for('world', worldid=worldid))
        

if __name__ == '__main__':
    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug = True)