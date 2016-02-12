#!/bin/sh
python fix_version.py
python setup.py bdist_wheel --universal
twine upload dist/* --config-file .pypirc
pip uninstall hdu --yes
pip install dist/hdu-0.0.0.0+experimentalversion-py2.py3-none-any.whl
