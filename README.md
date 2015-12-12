# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* This is the registration site for BonzAI Brawl.  Due to IT's inability to provide a Python dev environment, the main
   bonzai site (bonzai.cs.mtu.edu) written in PHP links to this one. Being able to write the registration site in Python
   allows a lot more flexibility and rapid development.

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
