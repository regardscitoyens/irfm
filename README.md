
## Prérequis

* Python 3
* virtualenvwrapper
* PostgreSQL

## Installation

```sh
$ git clone https://git.regardscitoyens.org/regardscitoyens/irfm.git
$ cd irfm
$ mkvirtualenv --python=$(which python3) irfm
$ pip install -e .
$ psql -c "create user irfm with password 'irfm';"
$ psql -c "create database irfm with owner irfm;"
$ irfm db upgrade
```

## Mise à jour

```sh
$ cd /path/to/irfm
$ workon irfm
$ git pull
$ irfm db upgrade
```

## Développement

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
