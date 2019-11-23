from flask import Flask, render_template, flash, redirect, url_for, session,request, logging
# from flask_mysqldb import MySQL
from functools import wraps
from passlib.hash import sha256_crypt 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.fields.html5 import TimeField


app = Flask(__name__)
app.config['SECRET_KEY'] = '_D_ONtT_ELlA_nyone_'

# Config MySQL
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '123456'
# app.config['MYSQL_DB'] = 'mybookingapp'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# # init MYSQL
# mysql = MySQL(app)

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/about")
def about():
	return render_template("about.html")

class RegistrationForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=5, max=30)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', 'Passwords do not match')
		])
	confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
	form =RegistrationForm(request.form)		#1
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		if result>0:
			flash("Username is already taken", 'danger')
			return render_template('register.html', form=form)

		# Create cursor
		cur = mysql.connection.cursor()

		# Execute query
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

		# Commit to DB
		mysql.connection.commit()

		# Close connection
		cur.close()

		flash('You are now registered and can log in', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', form=form)	#passing marked 1 form into render template register.html 

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']

		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
		if result > 0:
			data = cur.fetchone()
			password = data['password']

			if sha256_crypt.verify(password_candidate, password):
				session['logged_in']=True
				session['username']=username
				flash('You are now logged in', 'success')
				cur.close()
				return redirect(url_for('dashboard'))
			else:
				error = 'Invalid password'
				return render_template('login.html', error=error)
			cur.close()
		else:
			error = 'Username not found'
			return render_template('login.html', error=error)
	return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

class LoginForm(Form):
	city = StringField('City', [validators.Length(min=1, max=50)])
	name = StringField('Name Of Place', [validators.Length(min=1, max=50)])
	entrytime = TimeField('Entry Time', format='%H:%M')
	exittime = TimeField('Exit Time', format='%H:%M')

@app.route('/booking', methods=['GET', 'POST'])
def search_turf():
	form =LoginForm(request.form)
	if request.method=='POST' and form.validate():
		city = form.city.data
		name = form.name.data
		entrytime = form.entrytime.data
		exittime = form.exittime.data
		return redirect(url_for('dashboard'))
	return render_template('register1.html', form=form) 

# @app.route('/booking', methods=['GET','POST'])
# def search_turf():

# 	return render_template('1_search_place.html', loc=locations)

if __name__ == '__main__':
	app.run(debug=True)