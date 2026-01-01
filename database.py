from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} # SQLite를 위한 설정(기본적으로 하나의 스레드에서만 사용 가능하므로
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,
    bind=engine
    )

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()