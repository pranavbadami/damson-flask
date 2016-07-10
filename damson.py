from flask import Flask
from flask import request
from flask import render_template
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from subprocess import call
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/connect', methods=['GET', 'POST'])
def connect():
    form = ConnectionForm(request.form)
    if request.method == 'GET':
    	return render_template('connect.html', form=form, connected=False)
    
    if request.method == 'POST' and form.validate():
    	print form.ssid.data, form.password.data
        # call here
        connected = False
    	return render_template('connect.html', form=form, connected=connected, failed=True)

class ConnectionForm(Form):
    ssid = StringField('SSID')
    password = PasswordField('Password')
