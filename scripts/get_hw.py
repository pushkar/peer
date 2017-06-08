import sys
import json
import requests

assignment_short_name = 'td'
url_base = 'https://rldm.herokuapp.com/api/'
data_login = {}
data_login['username'] = ''
data_login['gtid'] = ''

url_login = url_base + 'login'
r = requests.post(url_login, data=data_login, headers=dict(Referer=url_login))

data = json.loads(r.text)
print("Login: %s %s" % (r.status_code, r.text))
print("Key is %s" % data['key'])

url_get_hw = url_base + 'codework/assignment/' + assignment_short_name
r = requests.get(url_get_hw, params=data)
print(r.url)
response = json.loads(r.text)
if 'error' in response:
    print("Error: %s" % response['error'])
    sys.exit(1)

score = {}
for hw_model in response:
    hw = hw_model['fields']

    student_id = hw['student']
    student_score = hw['score']
    if student_id not in score:
        score[student_id] = 0

    score[student_id] += student_score

for k, v in score.items():
    print(k, v)
