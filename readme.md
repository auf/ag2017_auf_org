# Gestion Assemblée Générale AUF

## Installation


### Pour développement

Créer une machine virtuelle avec `vagrant up`.

Puis, dans vagrant:

```shell script
    python3 -m venv /venvs/ag_py3
    . /venvs/ag_py3/bin/activate
    cd /vagrant
    pip install -r requirements/base.txt requirements/dev.txt
```

Lancer les tests:
```shell script
    . /venvs/ag_py3/bin/activate
    cd /vagrant
    pytest ag -ds ag.settings.tests
```
