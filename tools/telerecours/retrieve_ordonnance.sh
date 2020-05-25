#!/bin/bash

mkdir -p requetes
cd requetes

wget -O requetes.json --load-cookies=../telerecours.cookies https://citoyens.telerecours.fr/api/requetes

json_pp < requetes.json | grep '"id"' | awk '{print $3}' | sed 's/,//' | while read id ; do
    wget -O "requete_"$id".json" --load-cookies=../telerecours.cookies "https://citoyens.telerecours.fr/api/requetes/$id" ;
done

ls requete_*json | while read json ; do
    id=$(json_pp < $json | grep -B 10 "Notification d"  | grep id | sed 's/[^0-9]*//g') ;
    rid=$(echo $json | sed 's/[^0-9]//g');
    file=$(json_pp < $json | grep -A 30 $id | grep -B 5 '.doc'| grep fileApi | awk -F '"' '{print $4}' ) ;
    notif=$(json_pp < $json | grep AccuseNotification > /dev/null && echo "NotifOK") ;
    requete=$(json_pp < $json | grep numeroRequete  | awk -F '"' '{print $4}');
    defenseur=$(cat $json | sed 's/.*defendeur":"//' | sed 's/".*//')
    echo $rid";"$id";"$file";"$requete";"$defenseur";"$notif;
done > ../ordonnances.list

cat ordonnances.list | awk -F ';' '{if ( $6 == "NotifOK" && $3)
        print "wget -O ordonnance_"$1"_"$4".pdf --load-cookies=../telerecours.cookies " \
                    "--post-data='"'"'{\"origin\": \"TR_PJ_COPY\",\"typeEvent\": null,\"fileName\": \""$3"_doc.pdf\"}'"'"' " \
                    "--header=\"content-type: application/json\" " \
                    "https://citoyens.telerecours.fr/api/requetes/"$1"/events/"$2"/pieces/"$3"/download"}' | sh
