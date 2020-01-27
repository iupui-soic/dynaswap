#!/bin/sh
curl -X POST http://127.0.0.1:5000/DAR -d "{\"ip\": \"$(dig @resolver1.opendns.com ANYs.com +short)\"}"