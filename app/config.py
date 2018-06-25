import os

base_dir = os.path.abspath(os.path.dirname(__file__))
# 通用配置
class Config(object):
    # 秘钥
    SECRET_KEY = '124456'
    # 配置session的有效期
    SESSION_PERMANENT = True
    # 数据库的配置
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 邮件发送
    MAIL_SERVER = 'smtp.163.com'
    MAIL_USERNAME = '15518165352@163.com'
    MAIL_PASSWORD = 'aaa103525'
    # 使用本地bootstrap库
    BOOTSTRAP_SERVER_LOCAL = True
    # 文件上传
    MAX_CONTENT_LENGTH = 1024 * 1024 * 8
    UPLOADED_PHOTOS_DEST = os.path.join(base_dir, 'static/upload')
    #初始化函数，及时没有内容也建议写上, 可以在需要时使用同一接口
    @staticmethod
    def init_app(app):
        pass

# 开发环境配置
class DevelopConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'blog-dev.sqlite')

# 测试环境配置
class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'blog-test.sqlite')

# 生产环境配置
class ProductConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'blog.sqlite')


# 配置字典

config = {
    'develop': DevelopConfig,
    'testing': TestingConfig,
    'prodect': ProductConfig,
    'default': DevelopConfig
}
