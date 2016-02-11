#!/bin/sh
python setup.py bdist_wheel --universal
twine upload dist/* --config-file .pypirc
