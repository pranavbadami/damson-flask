import time
import requests
import uuid
import threading
import subprocess
#from fysom import Fysom

#global variables
hotspot = 1
current = {}
new = {}
payload = {'hotspot':'1'}
serial = 'abcd'


def update_rules(new, current):
    add_rule_user = {}
    remove_rule_user = {}

    #compared dicts and update the remove or add user rule dict. 
    for key in current:
        if key not in new:
            remove_rule_user[key] = current[key]

    for key in new:
        if key not in current:
            add_rule_user[key] = new[key]

    #set current to the new dict 
    current = new

    #Code to check the balance, if 0 add them to remove rule. 
    for key, value in current.iteritems():
        if value['balance'] <= 0:
            remove_rule_user[key] = current[key]

    return (remove_rule_user, add_rule_user)


def add_rule(rule):
    cmd = 'iptables -I internet 1 -t mangle -m mac --mac-source %s -j RETURN'
    p = subprocess.Popen(cmd % rule['mac'], shell=True)
    print "added", rule


def remove_rule(rule):
    cmd = 'iptables -D internet -t mangle -m mac --mac-source %s -j RETURN'
    p = subprocess.Popen(cmd % rule['mac'], shell=True)
    print "removed", rule


def update_bandwidth(current):

    #wait for ok, reset the data. 
    #TODO: Get data used.
    cmd = 'iptables -nvL internet -t mangle' 
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = p.stdout.read()
    ip_output = output.split('\n')
    for user in current:
        pk = user
        user = current[user]
        i = 0
        data = ''
        for ipo in ip_output:
            print "ipo", ipo
            if user['mac'].upper() in ipo:
                ipo_list = ipo.split(' ')
                ipo_list_fixed = [i for i in ipo_list if i]
                data = ipo_list_fixed[1]
                if 'K' in data:
                    data = int(data[:-1]) * 1000
                elif 'M' in data:
                    data = int(data[:-1]) * 1000000
                else:
                    data = int(data)

        print "data to upload", data

        up_payload = {  'uuid':uuid.uuid1().bytes, 
                        'data_used' : data, 
                        'hotspot': hotspot, 
                        'user': pk
                    }
        print "request to ", up_payload
        r = requests.post('http://damson.online/api/track', data=up_payload)
        print "message", r.json()
        if r.json() == 'Transaction successfully logged.':
            print "upload"
            #RESET the data on firewall


class BashIP(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print "up"
        for i in range(10,16):
            ip = "192.168.42.%d" %(i)
            subprocess.Popen('./rmtrack.sh %s' % (ip), shell=True)
            #Call bash script



if __name__ == "__main__":
    p = subprocess.Popen('bash iptables_flush.sh', shell=True)
    p.wait()
    p = subprocess.Popen('bash init-internet-chain.sh', shell=True)
    p.wait()
    p = subprocess.Popen('bash mark.sh', shell=True)
    p.wait()
    p = subprocess.Popen('bash sharing.sh', shell=True)
    p.wait()
    #get login url for the firewall
    # r = requests.get('http://damson.online/api/hotspots/', params = {'serial':serial})
    # if r.json():
    #     login_url = 'http://damson.online/api/hotspots' + r.json()[0]['url']
    # else:
    #     #TODO exit with an error that hotspot isn't registered
    #     print "wrong serial"

    # bash_ip = BashIP(1, "bash")
    # bash_ip.start()

    #get initial list and add
    add_rule_user = {}

    r = requests.get('http://damson.online/api/wifiusers', params = payload)
    user_list = r.json()
    for user in user_list:
        current[user['id']] = {'mac':user['mac'], 'balance':user['data_remaining']}
    for key in current:
        add_rule_user[key] = current[key]


    #function to add. 
    print "first user added", add_rule_user
    for rule in add_rule_user:
        rule_val = add_rule_user[rule]

        add_rule(rule_val)

    #loop
    while(1):
        new = {}
        r = requests.get('http://damson.online/api/wifiusers', params = payload)
        user_list = r.json()
        #GET request for a list of users
        for user in user_list:
            new[user['id']] = {'mac':user['mac'], 'balance':user['data_remaining']}
        
        remove_rule_user, add_rule_user = update_rules(new, current)
        
        #TODO update the firewall
        for rule in add_rule_user:
            rule_val = add_rule_user[rule]
            add_rule(rule_val)

        for rule in remove_rule_user:
            rule_val = remove_rule_user[rule]
            remove_user(rule_val)
        print remove_rule_user, add_rule_user
        #TODO track the current array usage, and transmit to the server. 
        update_bandwidth(current)

        time.sleep(2)








