#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib
from bs4 import BeautifulSoup
import sys
import codecs
sys.stdout = codecs.getwriter("UTF-8")(sys.stdout)

with open("data/codes.txt") as f:
    print u'"numéro de dossier","nom dossier","chambre","état de l\'instruction","requérant(s)","mandataire(s) requérant(s)","défendeur(s)","mandataire(s) défendeur(s)","date évènement","mesure évènement","acteur évènement","qualité évènement","délais évènement"'
    for line in f.readlines():
        (juridiction, dossier, cle) = line.replace(" \n", "").split(' - ')

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        resp = opener.open("https://sagace.juradm.fr/Authentification.aspx")
        soup = BeautifulSoup(resp.read(), "lxml")

        viewstate = soup.find('input', {"name": "__VIEWSTATE"})['value']#.replace('+', '%2B').replace("/", "%2F")
        viewstategenerator = soup.find('input', {"name": "__VIEWSTATEGENERATOR"})['value']

        login_data = urllib.urlencode({'TxtJuridiction': juridiction, 'TxtDossier': dossier, 'TxtAleaCle': cle, '__VIEWSTATE': viewstate, '__VIEWSTATEGENERATOR': viewstategenerator, "ibOk.x": 61, "ibOk.y": 11})
        request = urllib2.Request('https://sagace.juradm.fr/Authentification.aspx', data=login_data)
        request.get_method = lambda: "POST"

        resp = opener.open(request)

        soup = BeautifulSoup(resp.read(), "lxml")
        dossier = soup.select("td.txtgras2")[1].get_text(strip=True)
        chambre = soup.select("td.txt")[0].get_text(strip=True).replace("-Affectation :", "")
        etat = soup.select("td.txt")[1].get_text(strip=True)
        requerants = []
        requerants_mandataire = []
        defendeurs = []
        defendeurs_mandataire = []
        moments = []
        is_moments = False
        for tr in soup.select('.txttbl tr'):
            tds = tr.findAll('td', text=True)
            if (is_moments):
                date = tds[0].get_text(strip=True).split('/')[::-1]
                print('"'+dossier.replace(' - ', '","')+
                      '","'+chambre+
                      '","'+etat+
                      '","'+";".join(requerants)+
                      '","'+";".join(requerants_mandataire)+
                      '","'+";".join(defendeurs)+
                      '","'+";".join(defendeurs_mandataire)+'","'+
                      "-".join(date)+'","'+
                      (tds[1].get_text(strip=True) if (len(tds) > 1) else "") +'","'+
                      (tds[2].get_text(strip=True) if (len(tds) > 2) else "") +'","'+
                      (tds[3].get_text(strip=True) if (len(tds) > 3) else "") +'","'+
                      (tds[4].get_text(strip=True) if (len(tds) > 4) else "") +
                      '"')
            else:
                if tds[0].get_text(strip=True) == "Date":
                    is_moments = True
                elif tds[1].get_text(strip=True) == "Nom":
                    is_moments = False
                else:
                    if tds[0].get_text() == u'Requérant':
                        requerants.append(tds[1].get_text(strip=True))
                        if (len(tds) > 2):
                            requerants_mandataire.append(tds[2].get_text(strip=True))
                    elif tds[0].get_text() == u'Défendeur':
                        defendeurs.append(tds[1].get_text(strip=True))
                        if (len(tds) > 2):
                            defendeurs_mandataire.append(tds[2].get_text(strip=True))
