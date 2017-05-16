## Installation

### Prérequis

* Python 3 + headers (ie. python3-dev)
* virtualenvwrapper
* PostgreSQL (postgresql-server-dev-all)

### Nouvelle Installation

```sh
$ git clone https://git.regardscitoyens.org/regardscitoyens/irfm.git
$ cd irfm
$ mkvirtualenv --python=$(which python3) irfm
$ pip install -e .
$ sudo -u postgres psql -c "create user irfm with password 'irfm';"
$ sudo -u postgres psql -c "create database irfm with owner irfm;"
$ irfm db upgrade
$ irfm import_etapes
$ irfm import_nd
$ irfm import_adresses
```

### Mise à jour

```sh
$ cd /path/to/irfm
$ workon irfm
$ git pull
$ pip install -e .
$ irfm db upgrade
$ irfm import_etapes
$ irfm import_nd
$ irfm import_adresses
$ irfm clear_cache
```

### Déploiement

`irfm.irfm:app` est une application WSGI qui peut être servie avec n'importe quel serveur compatible (comme gunicorn).

L'application peut être configurée avec des variables d'environnement:

* `IRFM_CONFIG`: `irfm.config.EnvironmentConfig` (sauf si vous voulez utiliser votre propre module de configuration)
* `IRFM_DB_URL`: URL de connexion base de données, par défaut `postgresql://irfm:irfm@localhost:5432/irfm`
* `IRFM_DATA_DIR`: chemin vers un dossier où l'utilisateur exécutant l'application a les droits de lecture/écriture. Les uploads, fichiers générés et la clé secrète de l'application y seront stockés. **Ne pas laisser ce répertoire accessible au public.**
* `IRFM_PIWIK_HOST` et `IRFM_PIWIK_ID`: si définies, le code de tracking Piwik correspondant sera ajouté aux pages.
* `IRFM_ADMIN_EMAIL`: adresse e-mail d'expéditeur pour les mails envoyés
* `IRFM_ADMIN_PASSWORD`: mot de passe administrateur (nick `!rc`), voir ci-dessous pour le générer.
* Configuration mail:
    * `IRFM_MAIL_SERVER`, `IRFM_MAIL_PORT`: serveur SMTP, localhost:25 par défaut
    * `IRFM_MAIL_USERNAME`, `IRFM_MAIL_PASSWORD`, identifiants pour le serveur SMTP
    * `IRFM_MAIL_USE_TLS`, `IRFM_MAIL_USE_SSL`: options de sécurité, `False` par défaut
    * `IRFM_MAIL_SUPPRESS_SEND`: permet de désactivé totalement l'envoi de mails si positionné à `True`

Pour générer le mot de passe administrateur, exécuter `irfm password` dans le virtualenv de l'application puis saisir le mot de passe souhaité.  Attention, `IRFM_DATA_DIR` doit avoir la même valeur que lors de l'exécution de l'application WSGI, car la clé secrète qui y est stockée est utilisée pour hasher le mot de passe.

## Développement

### Exécution locale

```bash
$ cd /path/to/irfm
$ workon irfm
$ export IRFM_CONFIG=irfm.config.EnvironmentConfig
$ export IRFM_DEBUG=True
$ export IRFM_DEBUG_SQL=True
$ export IRFM_DB_URL=postgresql://irfm:irfm@localhost:5432/irfm
$ irfm runserver
```

### Génération de migrations

Après avoir modifié les modèles Python :

```bash
$ irfm db migrate -m <description>
$ irfm db upgrade
```

### Création de migration vierge

```bash
$ irfm db revision -m <description>
```
