import os
import socket
basedir = os.path.abspath(os.path.dirname(__file__))
hostname = socket.gethostname()

DEBUG = EMAIL_DEBUG = True
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://bonzai@localhost/bonzai'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# zaphod is lug, so these are settings for prod
if hostname == 'zaphod':
    DEBUG = True
    EMAIL_DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://bonzai:bonzai@localhost/bonzai'

SECRET_KEY = 'asdasdaosjhro i2p-c9u-19ci- q0sai-p19i-230iqwd-0i-'

UPLOADS_DEFAULT_DEST = os.path.join(basedir, 'uploads')
