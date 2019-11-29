from flask import Flask, render_template, flash, redirect, url_for, session,request, logging
from functools import wraps
from passlib.hash import sha256_crypt 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators,IntegerField
from wtforms.fields.html5 import TimeField
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="316723",
  database="mybookingapp"
)

app = Flask(__name__)
app.config['SECRET_KEY'] = '# @@#$_*+D?_!O!N!!!t^T%_EL lA_:n:y:on___e_'
# @@#$_*+D?_!O!N!!!t^T%_EL lA_:n:y:on___e_

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
		mycursor = mydb.cursor()
		mycursor.execute("SELECT * FROM users WHERE username = %s", [username])
		result = mycursor.fetchall()
		if len(result) > 0:
			flash("Username is already taken", 'danger')
			return render_template('register.html', form=form)

		# Create cursor
		# mycursor = mydb.cursor()
		# Execute query
		mycursor.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

		# Commit to DB
		mydb.commit()

		# Close connection
		mycursor.close()

		flash('You are now registered and can log in', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', form=form)	#passing marked 1 form into render template register.html 




@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']
		mycursor = mydb.cursor()

		# cur = mysql.connection.cursor()
		mycursor.execute("SELECT * FROM users WHERE username = %s", [username])
		result = mycursor.fetchall()
		if len(result) > 0:
			data = result[0]
			password = data[4]

			if sha256_crypt.verify(password_candidate, password):
				session['logged_in']=True
				session['username']=username
				session['userId']=data[0]
				flash('You are now logged in', 'success')
				mycursor.close()
				return redirect(url_for('dashboard'))
			else:
				error = 'Invalid password'
				mycursor.close()
				return render_template('login.html', error=error)
		else:
			error = 'Username not found'
			mycursor.close()
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
@is_logged_in
def dashboard():
	return render_template('dashboard.html')



class LoginForm(Form):
	Stadium_id = IntegerField('Stadium Id', [validators.required()])
	Stadium_name = StringField('Corresponding Stadium Name', [validators.Length(min=1, max=50)])

@app.route('/booking', methods=['GET', 'POST'])
@is_logged_in
def search_turf():
	mycursor = mydb.cursor()
	mycursor.execute("select * from cities_stadiums where booked is NULL")
	data = mycursor.fetchall()
	form =LoginForm(request.form)

	if request.method=='POST' and form.validate():
		Stadium_id = form.Stadium_id.data
		Stadium_name = form.Stadium_name.data
		session['Stadium_name'] = Stadium_name

		testvar = "SELECT booked FROM cities_stadiums WHERE id={}".format(str(Stadium_id))#new
		mycursor.execute(testvar)#new
		testdata = mycursor.fetchone()#new
		
		if testdata == None:#new
			flash("Sorry!Already booked!", 'danger')#new
			mycursor.close()#new
			return redirect(url_for('login'))#new
		else:#new	
			sql = "UPDATE cities_stadiums SET booked =" + str(session['userId']) + " WHERE id =" + str(Stadium_id)
			mycursor.execute(sql)
			mydb.commit()
			mycursor.close()
			param = [str(session['username']),str(session['Stadium_name'])]
			return render_template('summary.html', testList=param)
	return render_template('register1.html', form=form, value=data) 

if __name__ == '__main__':
	app.run(debug=True)
