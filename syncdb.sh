#!/bin/sh

#heroku autobus capture --app rldm DATABASE_URL
#rm latest.dump
#curl -o latest.dump `heroku pg:backups public-url --app rldm`
pg_restore --verbose --clean --no-acl --no-owner -h localhost -U pushkar -d rlspring2016 latest.dump
