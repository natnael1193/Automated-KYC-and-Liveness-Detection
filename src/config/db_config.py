from sqlmodel import SQLModel, create_engine, Session

engine = create_engine("mysql+pymysql://root:@localhost/automated_KYC", echo=True)
sessions = Session(engine)

def create_db_and_tables():
 SQLModel.metadata.create_all(engine)