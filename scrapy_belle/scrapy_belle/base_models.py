from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from scrapy.utils.project import get_project_settings


class InitEngine(object):

    def __init__(self):
        # settings = get_project_settings()
        self.engine = create_engine('sqlite:///url.db')

    def get_engine(self):
        return self.engine


engin = InitEngine().get_engine()
Base = declarative_base(bind=engin)
DBSession = sessionmaker(bind=engin)

# 在数据库中创建映射类对应的表
def create_tables():
    Base.metadata.create_all()


# 删除数据库中对应的映射类的表
def delete_tables():
    Base.metadata.drop_all()