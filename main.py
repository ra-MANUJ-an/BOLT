from flask import Flask, render_template, flash, redirect, url_for, session,request, logging
from flask_wtf import Form
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.fields.html5 import TimeField

app = Flask(__name__)
app.config['SECRET_KEY'] = '_D_ONtT_ELlA_nyone_'

class LoginForm(Form):
	name = StringField('City', [validators.Length(min=1, max=50)])
	name = StringField('Name Of Place', [validators.Length(min=1, max=50)])
	entrytime = TimeField('Entry Time', format='%H-%M-%S')
	exittime = TimeField('Exit Time', format='%H-%M-%S')

@app.route('/', methods=['GET', 'POST'])
def index():
	form =LoginForm(request.form)
	if form.validate():
		name = form.name.data
		entrytime = form.entrytime.data
		return render_template('register1.html')
	return render_template('register1.html', form=form) 

if __name__ == '__main__':
	app.run(debug=True)