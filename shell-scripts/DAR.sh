#!/bin/sh

# temporary server domain
SERVER="projects.brandonhaakenson.com:8000"
curl -X POST "$SERVER/DAR" -d "{\"ip\": \"$(dig @resolver1.opendns.com ANYs.com +short)\"}"