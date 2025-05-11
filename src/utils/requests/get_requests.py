from sqlmodel import select # type: ignore

from src.config.db_config import sessions
from src.utils.responses.responses import getResponse, notFoundResponse


def GetAllData(model, model_name):
    with sessions as session:
        data = session.exec(select(model)).all()
        return getResponse(data=data, model_name=model_name)


def GetDataById(model, id, model_name):
    with sessions as session:
        data = session.exec(select(model).where(model.id == id)).first()
        if data is None:
            return notFoundResponse()
        else:
            return getResponse(data=data, model_name=model_name)
