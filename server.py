import os
from flask import Flask, render_template, request
import random
import psycopg2
import psycopg2.extras

app = Flask(__name__)

def formatDate(date):
    #Get those months
    months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
    newDate = "";
    
    splitDate = str(date).split("-");
    newDate += months[int(splitDate[1])-1];
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
    
@app.route('/user/<username>')
def user(username):
    #Database connection
    conn = connectToDB()
    cur = conn.cursor()
    
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

if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug = True)