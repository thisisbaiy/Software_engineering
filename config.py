
SECRET_KEY = "****************"
# 数据库的配置信息
HOSTNAME = '127.0.0.1'
PORT     = '***'
DATABASE = 'software_engineering'
USERNAME = '123'
PASSWORD = '***'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI


# 邮箱配置
MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = "qq.com"
MAIL_PASSWORD = "***"
MAIL_DEFAULT_SENDER = "qq.com"