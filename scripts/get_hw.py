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
key = data['key']
print("Login: %s %s" % (r.status_code, r.text))
print("Key is %s" % key)

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
    iosolution_id = response['id']
    iosolution_info = response['solution']
    iopair_info = response['pair']
    student_info = response['student']

# Update IOSolutions
for response in responses:
    iosolution_id = response['id']
    url_update_sol = url_base + 'codework/solution/%s' % iosolution_id
    data = {
        'key': key,
        'score': 10,
        'submission': 'this is their new submission',
        'comments': 'these are some new comments',
    }
    r = requests.post(url_update_sol, data=data, headers=dict(Referer=url_login))
    r = json.loads(r.text)
    if 'error' in r:
        print("Error: %s" % responses['error'])
        sys.exit(1)
    print(r['message'])

