## Installation

### Prérequis

* Python 3 + headers (ie. python3-dev)
* virtualenvwrapper
* PostgreSQL

### Nouvelle Installation

```sh
$ git clone https://git.regardscitoyens.org/regardscitoyens/irfm.git
$ cd irfm
$ mkvirtualenv --python=$(which python3) irfm
$ pip install -e .
$ psql -c "create user irfm with password 'irfm';"
$ psql -c "create database irfm with owner irfm;"
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
