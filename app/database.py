from typing import Optional, List
from os import getenv

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from . import models


db_ip = getenv("DATABASE_IP")
if db_ip:
    SQLALCHEMY_DATABASE_URL = db_ip
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args = {
    "connect_timeout": 1
})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# temporary, for testing
def initBase(db: Session):
    engine = db.get_bind()
    try:
        models.CardModel.__table__.drop(engine)
    except:
        pass
    models.CardModel.__table__.create(engine)
    db_cards = [models.CardModel(
        id = 0,
        title = "A card",
        series = "Cardos",
        manufacturer = "Buraz Ltd.",
        serial_num = None,
    ),
    models.CardModel(
        id = 1,
        title = "Another card",
        series = "Cardos",
        manufacturer = "Buraz Ltd.",
        serial_num = None,
    ),
    models.CardModel(
        id = 2,
        title = "Superfastinsanekebab",
        series = "Čokolešnik",
        manufacturer = "A",
        serial_num = None,
    )]
    db.add_all(db_cards)
    db.commit()
    db.close()


class DBException(Exception):
    pass



def get_card_by_id(db: Session, cid: int) -> Optional[models.Card]:
    card = db.query(models.CardModel).filter(models.CardModel.id == cid).first()
    if card:
        return models.Card(**card.__dict__)
    return None


def get_all_cards(db: Session) -> List[models.Card]:
    return [models.Card(**card.__dict__) for card in db.query(models.CardModel).all()]


def insert_new_card(db: Session, new_card: models.CardNew) -> int:
    # new_id = db.query(models.CardModel.id).count()
    new_id = db.query(func.max(models.CardModel.id)).first()[0] + 1
    card_model = models.CardModel(
        id = new_id,
        title = new_card.title,
        series = new_card.series,
        manufacturer = new_card.manufacturer,
        serial_num = new_card.serial_num
    )
    db.add(card_model)
    db.commit()
    return new_id


def update_card(db: Session, cid: int, card: models.CardUpdate) -> None:
    card_model = db.query(models.CardModel).filter(models.CardModel.id == cid).first()
    if card_model == None:
        raise DBException
    if card.title != None:
        card_model.title = card.title
    if card.series != None:
        card_model.series = card.series
    if card.manufacturer != None:
        card_model.manufacturer = card.manufacturer
    if card.serial_num != None:
        card_model.serial_num = card.serial_num
    db.commit()


def delete_card(db: Session, cid: int) -> None:
    card_model = db.query(models.CardModel).filter(models.CardModel.id == cid)
    if card_model.first() == None:
        raise DBException
    card_model.delete()
    db.commit()


def test_connection(db: Session) -> bool:
    try:
        db.query(models.CardModel).first()
        return True
    except OperationalError:
        return False
