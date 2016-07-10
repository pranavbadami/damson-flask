from flask import Flask
from flask import request
from flask import render_template
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from subprocess import call
import time
app = Flask(__name__)

def net_string(ssid, password):
    base = "network={\n    ssid="+ssid+"\n    psk="+password+"\n    key_mgmt=WPA-PSK\n}"
    return base

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
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'r+') as conf:
            net_conf = conf.read()
            idx = net_conf.find("network=")
            new_conf = ""
            if idx:
                #overwrite networkf
                new_conf = net_conf[:idx] + net_string(form.ssid.data, form.password.data)
            else:
                new_conf = net_conf + "\n" + net_string(form.ssid.data, form.password.data)
            conf.seek(0)
            conf.write(new_conf)
            conf.truncate()
            conf.close()
        time.sleep(15)
        call(["ifdown", "--force", "wlan1"])
        call(["ifup", "wlan1"])

        # call here
        connected = True
    	return render_template('connect.html', form=form, connected=connected)

class ConnectionForm(Form):
    ssid = StringField('SSID')
    password = PasswordField('Password')
