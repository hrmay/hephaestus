import os
from flask import Flask, render_template, request
import random
import psycopg2
import psycopg2.extras

app = Flask(__name__)

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
    return render_template("index.html", world=world_results, world_desc = description[0][0], worldID = worldid);
    
@app.route('/article')
def articletest():
     return render_template("article.html");
     
def worldinfo(worldid):
    conn = connectToDB()
    cur = conn.cursor()
    
    #grab world info
    try:
        cur.execute("""SELECT world.Name, member.Username, COUNT(DISTINCT category.CategoryID), COUNT(DISTINCT article.ArticleID) FROM world JOIN member ON (world.CreatorID = member.UserID) JOIN category ON (world.WorldID = category.WorldID) JOIN article ON (world.WorldID = article.WorldID) WHERE world.WorldID = %s GROUP BY world.Name, member.Username;""", worldid)
    except:
        print("ERROR executing SELECT")
        print(cur.mogrify("""SELECT world.Name, member.Username, COUNT(DISTINCT category.CategoryID), COUNT(DISTINCT article.ArticleID) FROM world JOIN member ON (world.CreatorID = member.UserID) JOIN category ON (world.WorldID = category.WorldID) JOIN article ON (world.WorldID = article.WorldID) WHERE world.WorldID = %s GROUP BY world.Name, member.Username;""", worldid))
    world_results = cur.fetchall()
    
    #grab category names
    try:
        cur.execute("""SELECT category.Name, article.Name FROM category JOIN world ON (category.WorldID = world.WorldID) JOIN article ON (category.CategoryID = article.CategoryID) WHERE world.WorldID = %s;""", worldid)
    except:
        print("ERROR executing SELECT")
        print(cur.mogrify("""SELECT category.Name, article.Name FROM category JOIN world ON (category.WorldID = world.WorldID) JOIN article ON (category.CategoryID = article.CategoryID) WHERE world.WorldID = %s;""", worldid))
    category_results = cur.fetchall()
    
    #grab article names
#    try:
#        cur.execute("""SELECT article.Name FROM article JOIN world ON (article.WorldID = world.WorldID) WHERE world.WorldID = %s;""", worldid)
#    except:
#        print("ERROR executing SELECT")
#        print(cur.mogrify("""SELECT article.Name FROM article JOIN world ON (article.WorldID = world.WorldID) WHERE world.WorldID = %s;""", worldid))
#    article_results = cur.fetchall()
    
    ca_results = {}
    for category in category_results:
        print(category)
        if category[0] in ca_results:
            ca_results[category[0]].append(category[1])
        else:
            ca_results[category[0]] = [category[1]]

    results = [world_results, ca_results];
    return results
    
def worlddesc(worldid):
    conn = connectToDB()
    cur = conn.cursor()
    
    try:
        cur.execute("""SELECT LongDesc FROM world WHERE WorldID = %s;""", worldid)
    except:
        print("ERROR executing SELECT")
    
    description = cur.fetchall();
    return description

@app.route('/world/<worldid>')
def world(worldid):
    
    conn = connectToDB()
    cur = conn.cursor()

    results = worldinfo(worldid)
    
#    try:
#        cur.execute("""SELECT LongDesc FROM world WHERE WorldID = %s;""", worldid)
#    except:
#        print("ERROR executing SELECT")
    
    description = worlddesc(worldid)
    
    #grab world info
#    try:
#        cur.execute("""SELECT world.Name, world.LongDesc, member.Username, COUNT(DISTINCT category.CategoryID), COUNT(DISTINCT article.ArticleID) FROM world JOIN member ON (world.CreatorID = member.UserID) JOIN category ON (world.WorldID = category.WorldID) JOIN article ON (world.WorldID = article.WorldID) WHERE world.WorldID = %s GROUP BY world.Name, world.LongDesc, member.Username;""", worldid)
#    except:
#        print("ERROR executing SELECT")
#        print(cur.mogrify("""SELECT world.Name, world.LongDesc, member.Username, COUNT(DISTINCT category.CategoryID), COUNT(DISTINCT article.ArticleID) FROM world JOIN member ON (world.CreatorID = member.UserID) JOIN category ON (world.WorldID = category.WorldID) JOIN article ON (world.WorldID = article.WorldID) WHERE world.WorldID = %s GROUP BY world.Name, world.LongDesc, member.Username;""", worldid))
#    results = cur.fetchall()
#    
#    #grab category names
#    try:
#        cur.execute("""SELECT category.Name FROM category JOIN world ON (category.WorldID = world.WorldID) WHERE world.WorldID = %s;""", worldid)
#    except:
#        print("ERROR executing SELECT")
#        print(cur.mogrify("""SELECT category.Name FROM category JOIN world ON (category.WorldID = world.WorldID) WHERE world.WorldID = %s;""", worldid))
    
    #grab article names
    
    
    return render_template("world.html", world_info = results, world_description=description[0][0]);

@app.route('/world/<worldID>/<articlename>')
def article(worldid, articlename):
    #world(worldid, False);
    
    return render_template("article.html");
    
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
        
        color="#aaaaaa";
    
    return render_template("user.html", user_info = results, color=color);

@app.route('/signup')
def signup():
    return render_template('signup.html')

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
        results = cur.fetchall();
    except:
        print("Failed to execute the following: ")
        print(cur.mogrify("""SELECT username, email FROM member WHERE LOWER(username) = LOWER(%(username)s) OR LOWER(email) = LOWER(%(email)s);""", query))
        
    #Check
    u_free = True;
    e_free = True;
    
    if len(results) >= 1:
        for result in results:
            if result[0] == query['username']:
                u_exists = False;
            if results[1] == query['email']:
                e_exists = False;
        
    #Check that passwords match
    p_match = (query['password'] == query['confirm_password'])
    all_okay = (p_match and u_free and e_free)
    
    if (request.method == 'POST' and all_okay):
        try:
            cur.execute("""INSERT INTO member (username, email, joindate) VALUES (%(username)s, %(email)s, now());""", query)
        except:
            print("Failed to execute the following: ")
            print(cur.mogrify("""INSERT INTO member (username, email, joindate) VALUES (%(username)s, %(email)s, now());""", query))
            conn.rollback()
        conn.commit()
        
    return render_template("signup.html");

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug = True)