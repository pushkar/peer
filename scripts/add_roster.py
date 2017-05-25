import sys
import json
import requests

url_base = 'http://rldm.herokuapp.com/api/'
data_login = {}
data_login['username'] = 'pkolhe3'
data_login['gtid'] = '902285024'

url_login = url_base + 'login'
r = requests.post(url_login, data=data_login, headers=dict(Referer=url_login))

data = json.loads(r.text)
print("Login: %s %s" % (r.status_code, r.text))
print("Key is %s" % data['key'])

f = open('roster.csv', 'r')
students = f.read().split('\n')
f.close()
keys = students[0].split(',')

url_add_student = url_base + 'student/add'
for student in students[1:]:
    data_student = dict(zip(keys, student.split(',')))
    data_student['key'] = data['key']
    r = requests.post(url_add_student, data=data_student, headers=dict(Referer=url_add_student))
    response = json.loads(r.text)
    print(response)
    if 'error' in response:
        print("Error: %s" % response['error'])
        sys.exit(1)
    else:
        print("%s %s" % (r.status_code, response['message']))
