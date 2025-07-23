from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///audits.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    title = Column(String, nullable=False)
    auditor = Column(String, nullable=False)
    status = Column(String, nullable=False)

Base.metadata.create_all(engine)