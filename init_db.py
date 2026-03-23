from db_models_sqlalchemy import EvaluationORM, OpportunityORM, SourceORM
from db_session import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("database initialized")
