# export FLASK_ENV=development
from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt
app = Flask(__name__,template_folder='template')
app.secret_key = "testing"
client = pymongo.MongoClient("XXXXXXXXX Paste your connection string (SRV or Standard) XXXXX") # MongoDB
db = client.get_database('XXXX Name of your database XXXXX')
records = db.register
@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    if 'email' in session : 
        return redirect(url_for('logged_in'))
    if request.method == "POST": 
        email = request.form.get('email')
        password = request.form.get('password')
        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route("/signup",methods=['post', 'get'])
def signup():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname", None)
        email = request.form.get("email",None)
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template("signup.html", message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template("signup.html", message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template("signup.html", message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            return render_template("logged_in.html", email=new_email)
    return render_template("signup.html")
@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))
if __name__ == "__main__":
  app.run(debug=True)