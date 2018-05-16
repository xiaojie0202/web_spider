from sqlalchemy import Column, Integer,String
from .base_models import Base
from .base_models import DBSession
from .base_models import create_tables, delete_tables

# 代理表
# class Proxies(Base):
#     __tablename__ = 'proxies'
#     id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
#     protocol = Column(String(10), nullable=False)  # 协议 HTTP OR HTTPS
#     host = Column(String(20), nullable=False, unique=True)
#     port = Column(Integer, nullable=False)
#
#     def __repr__(self):
#         return '<Proxies protocol=%s, host=%s, port=%s >' % (self.protocol, self.host, self.port)
#
#     def __str__(self):
#         # {'http': 'http://183.159.84.219:18118'}
#         return '%s://%s:%s' % (self.protocol, self.host, self.port)

class RequestUel(Base):
    __tablename__ = 'requesturl'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    url = Column(String(256), nullable=False, unique=True)


    def __repr__(self):
        return '<RequestUrl<url=%s>' % self.url

class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    file = Column(String(128), nullable=False, unique=True)
    url = Column(String(256), nullable=False, unique=True)

create_tables()





