import sys
import json
import requests

assignment_short_name = 'td' # get from peer website
url_base = 'https://rldm.herokuapp.com/api/'
data_login = {
    'username': '',
    'gtid': ''
}

url_login = url_base + 'login'
r = requests.post(url_login, data=data_login, headers=dict(Referer=url_login))

data = json.loads(r.text)
print("Login: %s %s" % (r.status_code, r.text))
print("Key is %s" % data['key'])

url_get_hw = url_base + 'codework/assignment/' + assignment_short_name
r = requests.get(url_get_hw, params=data)
print(r.url)
print("You can call this url from a browser for the next 5 mins")
responses = json.loads(r.text)
if 'error' in responses:
    print("Error: %s" % responses['error'])
    print("Run again.")
    sys.exit(1)

for response in responses:
    student_info = response['student']
    iosolution_info = response['solution']
    iopair_info = response['pair']
