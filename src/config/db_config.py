from sqlmodel import SQLModel, create_engine, Session

engine = create_engine("mysql+pymysql://root:@localhost/fast_test", echo=True)
sessions = Session(engine)

def create_db_and_tables():
 SQLModel.metadata.create_all(engine)