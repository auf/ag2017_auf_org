pip-compile requirements/base.in --output-file requirements/base.txt
pip-compile requirements/dev.in --output-file requirements/dev.txt
pip-compile requirements/prod.in --output-file requirements/prod.txt
