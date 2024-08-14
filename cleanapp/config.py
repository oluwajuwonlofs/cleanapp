class Config(object):
    DATABASE_URI='sqlite:///:memory:'
    ADMIN_ID='1w456'
    


class ProductionConfig(Config):
    DATABASE_URI='mysql://user@localhost/foo'
    ADMIN_ID='asdfgh455^&*(AG78'
    SECRET_KEY='thisisproductionkey'


class DevelopmentConfig(Config):
    DATABASE_URI='mysql://:demo@localhost/foo'
    ADMIN_ID='thisisadminid'
    SECRET_KEY='thisisdevelopmentkey'
   