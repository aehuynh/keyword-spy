import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class GoogleSearchResult(Base):
    __tablename__ = 'google_search_results'
    id = Column(Integer, primary_key=True)
    keyword = Column(String(250), nullable=False)
    created_at = Column(Date, nullable=False)
    rank = Column(String(250), nullable=False)
    title = Column(String(250), nullable=False)
    link = Column(String(250), nullable=False)
    visible_url = Column(String(250), nullable=False)
    creative = Column(String(250), nullable=False)

class GoogleSearchAd(Base):
    __tablename__ = 'google_search_ads'
    id = Column(Integer, primary_key=True)
    keyword = Column(String(250), nullable=False)
    created_at = Column(Date, nullable=False)
    rank = Column(String(250), nullable=False)
    title = Column(String(250), nullable=False)
    link = Column(String(250), nullable=False)
    visible_url = Column(String(250), nullable=False)
    creative = Column(String(250), nullable=False)

def start_session():
    engine = create_engine('sqlite:///searchKeywordInfo.sqlite')
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
    return session()

def dict_to_google_search_result(keyword, date, col_dicts):
    session = start_session()
    for col_dict in col_dicts:
        search_result = GoogleSearchResult(**col_dict)
        search_result.created_at = date
        search_result.keyword = keyword
        session.add(search_result)
    session.commit()

def dict_to_google_search_ad(keyword, date, col_dicts):
    session = start_session()
    for col_dict in col_dicts:
        search_ad = GoogleSearchAd(**col_dict)
        search_ad.created_at = date
        search_ad.keyword = keyword
        session.add(search_ad)
    session.commit()