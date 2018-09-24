class Config:
    SECRET_KEY = 'insecure_key'

class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}