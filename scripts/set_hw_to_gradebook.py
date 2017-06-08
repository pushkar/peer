"""
Adds the scores to gradebook
1. Download gradebook template and store it as gradebook.csv
2. Download scores in csv format as hw.csv
3. Set keyname variables below
4. Run this script
"""

import csv

gradebook_file = "grades.csv"
student_username_key_in_gradebook = "Display ID"
hw_name_in_gradebook = "grade"
hw_file = "die_n.csv" # Download form rldm.herokuapp.com

scores_with_id = {}
scores = []

with open(hw_file) as f:
    hw_csv = csv.reader(f)
    for row in hw_csv:
        scores_with_id[row[0]] = row[3]

with open(gradebook_file, "r") as f:
    reader = csv.DictReader(f)
    for line in reader:
        if line[student_username_key_in_gradebook] in scores_with_id:
            _score = scores_with_id[line[student_username_key_in_gradebook]]
            line[hw_name_in_gradebook] = _score
            scores.append(line)
        else:
            print("Skipped %s" % line[student_username_key_in_gradebook])

with open(gradebook_file, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=scores[0].keys())

    writer.writeheader()
    for score in scores:
        writer.writerow(score)
