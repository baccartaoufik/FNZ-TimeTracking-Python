import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://root:root@localhost:3306/timetrackingdb')
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost:3306/timetrackingdb'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:0000@172.16.4.17:3306/timetrackingdb'
