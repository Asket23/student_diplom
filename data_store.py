# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_url_object

# схема БД
metadata = MetaData()
Base = declarative_base()

# Подключение к БД
engine = create_engine(db_url_object)
Base.metadata.create_all(engine)


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


# добавление записи в бд
def add_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()


# извлечение записей из БД
def user_verification(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(Viewed.profile_id == profile_id,
                                               Viewed.worksheet_id == worksheet_id).all()
    return True if from_bd else False