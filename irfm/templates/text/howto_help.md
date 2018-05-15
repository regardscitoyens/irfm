{% if current_step < ordres.ETAPE_DEMANDE_CADA %}

La première étape de notre action pour obtenir la transparence des frais de mandat des députés consiste à envoyer une demande de document à chaque parlementaire concerné par lettre recommandée avec accusé de réception. Malheureusement, notre petite équipe entièrement bénévole ne peut pas le faire pour tous les députés. **Mais vous pouvez nous aider à le faire !**

C'est simple : choisissez un parlementaire pour lequel la demande de document n'a pas encore été envoyée depuis la [liste des parlementaires](/parlementaires), cliquez sur le bouton « *Envoyer la demande* » et laissez-vous guider. Si vous ne savez pas lequel choisir, un parlementaire au hasard est affiché ci-contre.

<center><a class="btn btn-primary" href="/parlementaires">Trouver un-e député-e à solliciter</a> &nbsp; &nbsp; <a class="btn btn-primary" href="/hasard">Solliciter un-e député-e au hasard</a></center>

{% else %}

{% if current_step == ordres.ETAPE_DEMANDE_CADA %}
Nous avons transmis un recours auprès de la [Commission d'Accès aux Documents Administratifs (CADA)](http://cada.fr) pour chaque parlementaire n'ayant pas répondu positivement à notre demande. Celle-ci statuera vraisemblablement à la rentrée.
{% elif current_step == ordres.ETAPE_REQUETE_TA %}
Nous avons déposé une requête auprès du Tribunal Administratif pour chaque parlementaire n'ayant pas répondu positivement à notre demande.
{% endif %}

En attendant, vous pouvez contacter directement l'un des parlementaires ou l'un de leurs collaborateurs pour recueillir leur avis sur cette opération, et tenter de les convaincre de nous répondre favorablement.

<center><a class="btn btn-primary" href="/parlementaires?q=Demande%20CADA">Trouver un-e député-e à solliciter</a> &nbsp; &nbsp; <a class="btn btn-primary" href="/hasard">Solliciter un-e député-e au hasard</a></center>

{% endif %}

Notez bien que tous les parlementaires sont des élus de la Nation, vous êtes donc tout à fait en droit de solliciter un élu d'une autre circonscription que celle de votre domicile.
