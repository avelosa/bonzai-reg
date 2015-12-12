# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* This is the registration site for the 2015 BonzAI Brawl.

### How to Install ###

* Set up virtualenvwrapper
* Make a new virtualenv
* pip install -r stable-req.txt
* python run.py db upgrade
* python run.py runserver
* wait for registrants to apply

## Layout

This app is broken into 4 main parts:

* models (db models)
* forms (simple data processing)
* views (hooking the backend to the frontend)
* templates (frontend)
