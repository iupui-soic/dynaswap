#!/bin/sh

# temporary server domain
SERVER="https://dynaswap.info"
curl -X POST "$SERVER/DAR" -d "{\"ip\": \"$(dig @resolver1.opendns.com ANYs.com +short)\"}"