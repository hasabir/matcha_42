#!/bin/sh


python -m venv djang_venv
source djang_venv/bin/activate
pip install --upgrade pip
pip install psycopg2-binary Django django-debug-toolbar dj-database-url django-environ   

