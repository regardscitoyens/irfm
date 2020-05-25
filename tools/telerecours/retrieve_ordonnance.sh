#!/bin/bash

#echo "select parlementaire_id, attachment from actions where attachment LIKE '%requete%';" | sudo -u irfm psql irfm | grep pdf | sed 's/| requete-ta-//'  | sed 's/.pdf//' | awk '{print $1"-"$2}' > id_slug.list

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
done > ../ordonnances.csv

cat ordonnances.csv | awk -F ';' '{if ( $6 == "NotifOK" && $3)
        print "wget -O ordonnance_"$1"_"$4".pdf --load-cookies=../telerecours.cookies " \
                    "--post-data='"'"'{\"origin\": \"TR_PJ_COPY\",\"typeEvent\": null,\"fileName\": \""$3"_doc.pdf\"}'"'"' " \
                    "--header=\"content-type: application/json\" " \
                    "https://citoyens.telerecours.fr/api/requetes/"$1"/events/"$2"/pieces/"$3"/download"}' | sh

cd -
sed -i 's/é/e/g' ordonnances.csv
sed -i 's/É/E/g' ordonnances.csv
sed -i 's/È/E/g' ordonnances.csv
sed -i 's/è/e/g' ordonnances.csv
sed -i 's/ç/c/g' ordonnances.csv
sed -i 's/ë/e/g' ordonnances.csv
sed -i 's/ô/o/g' ordonnances.csv
cat id_slug.list | sed 's/ //g' | awk -F '-' '{printf "echo \""$0";\"$( grep -i "$2" ordonnances.csv | grep -i "$3 ; if ($4) printf " | grep -i "$4 ; if ($5) printf " | grep -i "$5 ; printf " && echo \";"$1"\") ;\n"}'  | sh > ordonnances_attachment.csv
