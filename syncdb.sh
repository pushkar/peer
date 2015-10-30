#!/bin/sh

heroku pg:backups capture --app oms-fall2015 HEROKU_POSTGRESQL_BROWN_URL
rm latest.dump
curl -o latest.dump `heroku pg:backups public-url --app oms-fall2015`
pg_restore --verbose --clean --no-acl --no-owner -h localhost -U pushkar -d peerfall2015 latest.dump
