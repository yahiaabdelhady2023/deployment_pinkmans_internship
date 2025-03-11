# flask_app/app/config.py

class Config:
    DEBUG = True
    SECRET_KEY = 'your_secret_key_here'
    DATABASE_URI = 'sqlite:///your_database.db'

class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URI = 'postgresql://user:password@localhost/prod_db'

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = 'sqlite:///dev_database.db'
