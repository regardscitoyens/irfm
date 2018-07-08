#!/bin/bash

id=$$
TMP=/tmp/$id/
mkdir -p $TMP
JURIDICTION=$1
DOSSIER=$2
CLE=$3

curl -s -L -c $TMP/cookie.jar https://sagace.juradm.fr/Authentification.aspx > $TMP/authentification.aspx
VIEWSTATE=$(grep '__VIEWSTATE"' $TMP/authentification.aspx | sed 's/.*value="//' | sed 's/".*//' | sed 's/\+/%2B/g' | sed 's/\//%2F/g')
VIEWSTATEGENERATOR=$(grep '__VIEWSTATEGENERATOR"' $TMP/authentification.aspx | sed 's/.*value="//' | sed 's/".*//')

curl -s -L -b $TMP/cookie.jar -H 'Referer: https://sagace.juradm.fr/Authentification.aspx' --data '__VIEWSTATE='$VIEWSTATE'&__VIEWSTATEGENERATOR='$VIEWSTATEGENERATOR'&TxtJuridiction='$JURIDICTION'&TxtDossier='$DOSSIER'&TxtAleaCle='$CLE'&ibOk.x=61&ibOk.y=11' 'https://sagace.juradm.fr/Authentification.aspx' > $TMP/dossier.html
if ! grep ">$DOSSIER" $TMP/dossier.html ; then
  echo "ERROR: $DOSSIER" ;
fi | sed 's/<[^>]*>//g'

rm -rf $TMP
