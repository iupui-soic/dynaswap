#!/bin/sh

# temporary server domain
SERVER="https://dynaswap.info"
curl -X POST "$SERVER/DAR" -d "{\"ip\": \"$(curl https://diagnostic.opendns.com/myip)\"}"
