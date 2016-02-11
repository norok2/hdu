#!/bin/sh
python setup.py bdist_wheel --universal
twine upload dist/*

git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .pypirc' --prune-empty --tag-name-filter cat -- --all
