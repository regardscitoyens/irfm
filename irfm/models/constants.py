# -*- coding: utf-8 -*-


import datetime


MOIS_RELEVES = 6
DEBUT_ACTION = datetime.date(2017, 5, 16)

_m = DEBUT_ACTION.month - MOIS_RELEVES
_y = DEBUT_ACTION.year
while _m < 1:
    _m = _m + 12
    _y = _y - 1

DEBUT_RELEVES = datetime.date(_y, _m, DEBUT_ACTION.day)

# Délais pour la relance de citoyens en jours
DELAI_RELANCE = 7
DELAI_REPONSE = 2

# Etapes

ETAPE_DOC_PUBLIE = -31
ETAPE_DOC_MASQUE = -30
ETAPE_COM_PUBLIE = -21
ETAPE_COM_A_MODERER = -20
ETAPE_COURRIEL = -10
ETAPE_NA = 0
ETAPE_A_ENVOYER = 10
ETAPE_A_CONFIRMER = 15
ETAPE_ENVOYE = 20
ETAPE_AR_RECU = 30
ETAPE_REPONSE_POSITIVE = 40
ETAPE_REPONSE_NEGATIVE = 50
ETAPE_DEMANDE_CADA = 60
ETAPE_INCOMPETENCE_CADA = 65
ETAPE_REQUETE_TA = 70
ETAPE_INCOMPETENCE_TA = 75
ETAPE_ATTENTE_CE = 79
ETAPE_APPEL_CE = 80
ETAPE_REJET_CE = 85
ETAPE_ATTENTE_TA = 90
ETAPE_ORDONNANCE_TA = 95
ETAPE_REQUETE_CEDH = 100

ETAPES = [
    {
        'ordre': ETAPE_DOC_PUBLIE,
        'label': 'Document',
        'description': """
            Un document nous a été transmis par le parlementaire.
        """,
        'couleur': '#33aa33',
        'icone': 'paperclip',
        'hidden': False,
        'alerte': False,
    },
    {
        'ordre': ETAPE_DOC_MASQUE,
        'label': 'Document (non publié)',
        'description': """
            Un document nous a été transmis par le parlementaire.
        """,
        'couleur': '#ccaa66',
        'icone': 'paperclip',
        'hidden': True,
        'alerte': False,
    },
    {
        'ordre': ETAPE_COM_PUBLIE,
        'label': 'Commentaire',
        'description': """
            Un citoyen a interpelé le parlementaire sur la transparence
            de son indemnité.
        """,
        'couleur': '#bbbbbb',
        'icone': 'commenting',
        'hidden': False,
        'alerte': False,
    },
    {
        'ordre': ETAPE_COM_A_MODERER,
        'label': 'Commentaire (non publié)',
        'description': """
            Un citoyen a interpelé le parlementaire sur la transparence
            de son indemnité. Le commentaire doit être modéré avant
            publication.
        """,
        'couleur': '#bb6666',
        'icone': 'commenting',
        'hidden': True,
        'alerte': False,
    },
    {
        'ordre': ETAPE_COURRIEL,
        'label': 'E-mail envoyé',
        'description': """
            La demande a été envoyée par Regards Citoyens au parlementaire
            par e-mail.
        """,
        'couleur': '#66aadd',
        'icone': 'at',
        'hidden': False,
        'alerte': False,
    },
    {
        'ordre': ETAPE_NA,
        'label': 'N/A',
        'description': '',
        'couleur': '',
        'icone': '',
        'hidden': True,
        'alerte': False,
    },
    {
        'ordre': ETAPE_A_ENVOYER,
        'label': 'À envoyer',
        'description': """
            Aucun citoyen n'a encore pris en charge l'envoi d'une demande
            d'accès aux relevés de comptes du parlementaire.
        """,
        'couleur': '#bbbbbb',
        'icone': 'envelope-open',
        'hidden': False,
        'alerte': False,
    },
    {
        'ordre': ETAPE_A_CONFIRMER,
        'label': 'Pris en charge',
        'description': """
            Un citoyen a souhaité se charger de l'envoi de la demande, mais
            nous n'avons pas encore confirmation de cet envoi.
        """,
        'couleur': '#aaaaff',
        'icone': 'clock-o',
        'hidden': False,
        'alerte': False,
    },
    {
        'ordre': ETAPE_ENVOYE,
        'label': 'Envoyé',
        'description': """
            La demande d'accès aux relevés de comptes du parlementaire a été
            envoyée, mais nous n'avons pas encore d'accusé de réception.
        """,
        'couleur': '#8888dd',
        'icone': 'envelope',
        'hidden': False,
        'alerte': False,
    },
    {
        'ordre': ETAPE_AR_RECU,
        'label': 'AR reçu',
        'description': """
            Le parlementaire a bien reçu la demande d'accès à ses relevés de
            comptes, nous avons reçu son accusé de réception.
        """,
        'couleur': '#4444bb',
        'icone': 'check',
        'hidden': False,
        'alerte': False,
    },
    {
        'ordre': ETAPE_REPONSE_POSITIVE,
        'label': 'Réponse positive',
        'description': """
            Le parlementaire nous a transmis les relevés de compte demandés
            ou nous a annoncé son intention de le faire.
        """,
        'couleur': '#66bb66',
        'icone': 'heart',
        'hidden': False,
        'alerte': True,
    },
    {
        'ordre': ETAPE_REPONSE_NEGATIVE,
        'label': 'Réponse négative',
        'description': """
            Le parlementaire a refusé de nous transmettre ses relevés de
            compte, soit explicitement, soit par voie de presse, soit à
            l'expiration d'un délai d'un mois après réception de la demande.
        """,
        'couleur': '#bb6666',
        'icone': 'thumbs-down',
        'hidden': False,
        'alerte': True,
    },
    {
        'ordre': ETAPE_DEMANDE_CADA,
        'label': 'Demande CADA',
        'description': """
            Suite au refus ou a l'absence de réponse du parlementaire, nous
            avons transmis la demande d'accès aux relevés de compte à la
            Commission d'Accès aux Documents Administratifs.
        """,
        'couleur': '#eebb44',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': True
    },
    {
        'ordre': ETAPE_INCOMPETENCE_CADA,
        'label': 'Incompétence CADA',
        'description': """
            Suite au refus ou a l'absence de réponse du parlementaire, nous
            avons transmis la demande d'accès aux relevés de compte à la
            Commission d'Accès aux Documents Administratifs.  Celle-ci s'est
            déclarée incompétente pour répondre à notre demande.
        """,
        'couleur': '#bbbbbb',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': False
    },
    {
        'ordre': ETAPE_REQUETE_TA,
        'label': 'Requête TA',
        'description': """
            Suite à la déclaration d'incompétence de la CADA, nous avons
            transmis la requête au tribunal administratif.
        """,
        'description_mail': """
            Suite au refus ou a l'absence de réponse du parlementaire, nous
            avons transmis la demande d'accès aux relevés de compte à la
            Commission d'Accès aux Documents Administratifs.  Celle-ci s'est
            déclarée incompétente pour répondre à notre demande.

            Nous avons donc transmis la requête au tribunal administratif.
        """,
        'couleur': '#eebb44',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': True
    },
    {
        'ordre': ETAPE_INCOMPETENCE_TA,
        'label': 'Incompétence TA',
        'description': """
            Suite à notre sollicitation, le tribunal administratif s'est déclaré
            incompétent en matière de transparence des Frais de mandat.
        """,
        'description_mail': """
            Suite au refus ou a l'absence de réponse du parlementaire, nous
            avons attaqué les parlementaires au Tribunal Administratif de
            Paris. Celui-ci s'est déclaré incompétent pour répondre à notre
            demande.

            Nous avons donc fait appel de cette décision à Conseil d'État.
        """,
        'couleur': '#bbbbbb',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': False
    },
    {
        'ordre': ETAPE_APPEL_CE,
        'label': 'Appel CE',
        'description': """
            Suite à la déclaration d'incompétence du Tribunal Administratif,
            nous avons fait appel auprès du Conseil d'État.
        """,
        'description_mail': """
            Le Tribunal Administratif de Paris s'étant déclaré incompétent,
            nous avons fait appel de cette décision auprès du Conseil d'État
            afin de faire valoir notre droit à l'information auprès de la plus
            haute juridiction administrative.
        """,
        'couleur': '#eebb44',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': True
    },
    {
        'ordre': ETAPE_ATTENTE_CE,
        'label': 'Attente CE',
        'description': """
            Attente de la décision du Conseil d'État
        """,
        'description_mail': """
            Le Tribunal Administratif de Paris a fait le choix d'attendre
            la décision du Conseil d'État sur notre appel concernant notre
            différent avec deux autres parlementaires pour prendre une
            décision sur ce dossier.
        """,
        'couleur': '#bbbbbb',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': True
    },
    {
        'ordre': ETAPE_REJET_CE,
        'label': 'Rejet CE',
        'description': """
            Le Conseil d'État annule la décision du Tribunal Administratif
            mais rejette notre demande de transparence.
        """,
        'description_mail': """
            Le Conseil d'État annule la décision du Tribunal Administratif
            qui aurait du se déclarer compétent pour juger de notre demande.
            En revanche, sur le fond, il rejette notre demande pour cause
            de souveraineté nationale.
        """,
        'couleur': '#ee4444',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': True
    },
    {
        'ordre': ETAPE_ATTENTE_TA,
        'label': 'Attente TA',
        'description': """
            Attente du jugement du TA
        """,
        'description_mail': """
            Suite à la décision du Conseil d'État, le Tribunal Administratif
            doit juger ce dossier. Il devrait rejeter notre demande.
        """,
        'couleur': '#bbbbbb',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': True
    },
    {
        'ordre': ETAPE_ORDONNANCE_TA,
        'label': 'Ordonnance TA',
        'description': """
            Ordonnance du TA
        """,
        'description_mail': """
            Suite à la décision du Conseil d'État, le Tribunal Administratif
            s'est conformé à cette décision en statuant par odonnance
        """,
        'couleur': '#ee4444',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': True
    },
    {
        'ordre': ETAPE_REQUETE_CEDH,
        'label': 'Requête CEDH',
        'description': """
            Requête auprès de la CEDH
        """,
        'description_mail': """
            Suite à la décision du Conseil d'État, nous avons déposé
            une requête auprès de la CEDH pour violation du droit à 
            l'information
        """,
        'couleur': '#eebb44',
        'icone': 'balance-scale',
        'hidden': False,
        'alerte': True
    }


]

ETAPES_BY_ORDRE = {e['ordre']: e for e in ETAPES}


#
# Lors de la modification de ces énumérations, penser à créer une migration DB
# pour mettre à jour les types ENUM correspondants en base de données.
#

CHAMBRES = {
    'AN': 'Assemblée nationale',
    'SEN': 'Sénat',
}

SEXES = {
    'F': 'Femme',
    'H': 'Homme',
}
