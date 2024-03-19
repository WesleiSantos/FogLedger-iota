#!/bin/bash

docker build -f ./iota/iota.dockerfile -t hornet ./iota
docker build -f ./iota/iota-explorer-api.dockerfile -t iotaledger/explorer-api ./iota
docker build -f ./iota/iota-explorer-web-app.dockerfile -t iotaledger/explorer-webapp ./iota

