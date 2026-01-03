# Todo App - FastAPI 입문 프로젝트

## 프로젝트 개요

**목표**: FastAPI + SQLAlchemy 기본 CRUD 익히기
**예상 소요 시간**: 2-3시간
**난이도**: 초급

### 배울 수 있는 것
- FastAPI 프로젝트 구조
- SQLAlchemy 모델 정의
- Pydantic 스키마
- 기본 CRUD API (Create, Read, Update, Delete)

---

## 완성된 API 미리보기

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/todos` | 전체 할일 목록 |
| GET | `/todos/{id}` | 특정 할일 조회 |
| POST | `/todos` | 할일 생성 |
| PUT | `/todos/{id}` | 할일 수정 |
| DELETE | `/todos/{id}` | 할일 삭제 |

---

## Step 1: 프로젝트 폴더 생성

### 1.1 터미널에서 폴더 만들기

```bash
# 프로젝트 폴더 생성
mkdir todo-app
cd todo-app

# 가상환경 생성 (Python 3.11 기준)
python -m venv venv

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
# venv\Scripts\activate
```

### 1.2 필수 패키지 설치

```bash
pip install fastapi uvicorn sqlalchemy
```

**각 패키지 역할:**
- `fastapi`: 웹 프레임워크
- `uvicorn`: ASGI 서버 (FastAPI 실행용)
- `sqlalchemy`: ORM (DB 연결)

### 1.3 requirements.txt 생성

파일 생성: `todo-app/requirements.txt`

```bash
# 방법 1: 직접 파일 생성 후 내용 작성
touch requirements.txt

# 방법 2: echo로 한 번에 생성
echo -e "fastapi\nuvicorn\nsqlalchemy" > requirements.txt

# 방법 3: pip freeze 사용 (이미 설치된 패키지 기준)
pip freeze > requirements.txt
```

**파일 내용:**
```
fastapi
uvicorn
sqlalchemy
```

---

## Step 2: 프로젝트 구조 만들기

### 2.1 폴더 구조

```
todo-app/
├── main.py          ← FastAPI 앱 (여기서 시작!)
├── database.py      ← DB 연결 설정
├── models.py        ← SQLAlchemy 모델
├── schemas.py       ← Pydantic 스키마
└── requirements.txt
```

**왜 이렇게 나누나요?**
- `main.py`: API 엔드포인트 정의
- `database.py`: DB 연결 로직 분리
- `models.py`: DB 테이블 구조
- `schemas.py`: API 요청/응답 형식

> BetaShift처럼 routers/, models/ 폴더로 나누지 않는 이유:
> 간단한 프로젝트는 파일 하나씩으로 충분합니다!

---

## Step 3: database.py 작성

파일 생성: `todo-app/database.py`

```python
"""
Database Configuration
SQLite 연결 설정 (가장 간단한 DB)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# =============================================================================
# 1. DB 연결 URL
# =============================================================================
# SQLite: 파일 하나로 동작하는 간단한 DB
# todo.db 파일이 자동 생성됨
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

# =============================================================================
# 2. Engine 생성
# =============================================================================
# Engine = DB와의 연결을 관리하는 객체
# connect_args: SQLite 전용 설정 (멀티스레드 허용)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# =============================================================================
# 3. Session 팩토리
# =============================================================================
# Session = DB와 대화하는 창구
# autocommit=False: 명시적으로 commit() 해야 저장됨
# autoflush=False: 쿼리 전 자동 flush 안 함
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# =============================================================================
# 4. Base 클래스
# =============================================================================
# 모든 모델이 이 클래스를 상속받음
Base = declarative_base()

# =============================================================================
# 5. DB 세션 의존성
# =============================================================================
def get_db():
    """
    FastAPI 의존성 주입용 함수

    - 요청마다 새 세션 생성
    - 요청 끝나면 자동으로 세션 닫기
    - yield 키워드로 Generator 사용
    """
    db = SessionLocal()
    try:
        yield db  # 여기서 db를 "빌려줌"
    finally:
        db.close()  # 요청 끝나면 무조건 실행
```

### 코드 설명

**Q: SQLite가 뭐예요?**
- 파일 하나로 동작하는 경량 DB
- 설치 필요 없음 (Python에 내장)
- 학습용/소규모 프로젝트에 적합

**Q: yield가 뭐예요?**
```python
def get_db():
    db = SessionLocal()  # 1. 세션 생성
    try:
        yield db         # 2. 세션을 빌려줌 (여기서 일시정지)
    finally:
        db.close()       # 3. 요청 끝나면 세션 닫기
```

---

## Step 4: models.py 작성

파일 생성: `todo-app/models.py`

```python
"""
SQLAlchemy Models
DB 테이블 구조 정의
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from database import Base

# =============================================================================
# Todo 모델
# =============================================================================
class Todo(Base):
    """
    할일 테이블

    __tablename__: 실제 DB에 생성될 테이블 이름
    """
    __tablename__ = "todos"

    # Primary Key: 각 할일의 고유 ID
    # autoincrement: 자동으로 1, 2, 3... 증가
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 할일 제목 (필수)
    # nullable=False: NULL 허용 안 함
    title = Column(String(100), nullable=False)

    # 할일 설명 (선택)
    # nullable=True (기본값): NULL 허용
    description = Column(String(500))

    # 완료 여부
    # default=False: 새로 생성하면 기본값 False
    completed = Column(Boolean, default=False)

    # 생성 일시
    # default=datetime.now: 생성 시 현재 시간 자동 저장
    created_at = Column(DateTime, default=datetime.now)

    # 수정 일시
    # onupdate=datetime.now: 수정할 때마다 자동 갱신
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

### 코드 설명

**Column 타입:**
| 타입 | 설명 | 예시 |
|------|------|------|
| `Integer` | 정수 | 1, 2, 100 |
| `String(n)` | 문자열 (최대 n자) | "할일1" |
| `Boolean` | True/False | True |
| `DateTime` | 날짜와 시간 | 2026-01-01 12:30:00 |

**주요 옵션:**
| 옵션 | 설명 |
|------|------|
| `primary_key=True` | 기본키 (고유 식별자) |
| `nullable=False` | NULL 불가 (필수값) |
| `default=값` | 기본값 설정 |
| `onupdate=값` | UPDATE 시 자동 갱신 |

---

## Step 5: schemas.py 작성

파일 생성: `todo-app/schemas.py`

```python
"""
Pydantic Schemas
API 요청/응답 데이터 형식 정의
"""

from datetime import datetime

from pydantic import BaseModel

# =============================================================================
# 생성용 스키마
# =============================================================================
class TodoCreate(BaseModel):
    """
    할일 생성 시 필요한 데이터

    - id는 DB가 자동 생성하므로 여기 없음
    - completed는 기본값 False
    - created_at, updated_at은 DB가 자동 생성
    """
    title: str
    description: str | None = None  # 선택 (없으면 None)
    completed: bool = False         # 선택 (없으면 False)


# =============================================================================
# 수정용 스키마
# =============================================================================
class TodoUpdate(BaseModel):
    """
    할일 수정 시 필요한 데이터

    - 모든 필드 선택사항 (변경할 것만 보내면 됨)
    - updated_at은 DB가 자동 갱신
    """
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


# =============================================================================
# 응답용 스키마
# =============================================================================
class TodoResponse(BaseModel):
    """
    할일 조회 응답 형식

    - DB에서 가져온 모든 필드 포함
    - model_config: SQLAlchemy 객체 → Pydantic 변환 허용
    """
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# 삭제 응답용 스키마
# =============================================================================
class TodoDeleteResponse(BaseModel):
    """
    할일 삭제 후 응답 형식

    - message: 삭제 완료 메시지
    - todos: 삭제 후 남은 전체 할일 목록
    """
    message: str
    todos: list[TodoResponse]
```

### 코드 설명

**왜 스키마가 4개?**

```
TodoCreate         → POST 요청 (생성할 때)
TodoUpdate         → PUT 요청 (수정할 때)
TodoResponse       → 응답 (조회할 때)
TodoDeleteResponse → DELETE 응답 (삭제 후 전체 목록 반환)
```

**`str | None` 문법:**
```python
description: str | None = None
# Python 3.10+ 문법
# "str이거나 None일 수 있고, 기본값은 None"

# 예전 방식 (동일한 의미)
from typing import Optional
description: Optional[str] = None
```

---

## Step 6: main.py 작성

파일 생성: `todo-app/main.py`

```python
"""
Todo App - FastAPI Main Application
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import Todo
from schemas import TodoCreate, TodoUpdate, TodoResponse, TodoDeleteResponse

# =============================================================================
# 테이블 생성
# =============================================================================
# 앱 시작 시 models.py에 정의된 테이블들을 DB에 생성
Base.metadata.create_all(bind=engine)

# =============================================================================
# FastAPI 앱 생성
# =============================================================================
app = FastAPI(
    title="Todo App",
    description="FastAPI 입문 프로젝트",
    version="1.0.0"
)

# =============================================================================
# API 엔드포인트
# =============================================================================

# -----------------------------------------------------------------------------
# 1. 전체 조회 (GET /todos)
# -----------------------------------------------------------------------------
@app.get("/todos", response_model=list[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    """
    모든 할일 목록을 조회합니다.

    - response_model: 응답 형식 지정
    - list[TodoResponse]: TodoResponse의 리스트
    """
    todos = db.query(Todo).all()
    return todos


# -----------------------------------------------------------------------------
# 2. 단건 조회 (GET /todos/{id})
# -----------------------------------------------------------------------------
@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    특정 할일을 조회합니다.

    - todo_id: URL 경로에서 받는 파라미터
    - 없으면 404 에러 반환
    """
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


# -----------------------------------------------------------------------------
# 3. 생성 (POST /todos)
# -----------------------------------------------------------------------------
@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """
    새 할일을 생성합니다.

    - todo: 요청 본문 (JSON → TodoCreate로 자동 변환)
    - status_code=201: 생성 성공 시 201 반환

    DB 저장 과정:
    1. model_dump(): Pydantic → dict 변환
    2. Todo(**dict): dict → SQLAlchemy 객체
    3. add(): 세션에 추가 (아직 저장 안 됨)
    4. commit(): 실제 DB에 저장
    5. refresh(): DB에서 최신 값 다시 읽기 (id 등)
    """
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


# -----------------------------------------------------------------------------
# 4. 수정 (PUT /todos/{id})
# -----------------------------------------------------------------------------
@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    db: Session = Depends(get_db)
):
    """
    할일을 수정합니다.

    - exclude_unset=True: 클라이언트가 보낸 필드만 추출
    - setattr(): 객체의 속성값 변경
    """
    # 1. 기존 데이터 조회
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # 2. 변경할 필드만 추출
    update_data = todo.model_dump(exclude_unset=True)

    # 3. 각 필드 업데이트
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    # 4. 저장
    db.commit()
    db.refresh(db_todo)
    return db_todo


# -----------------------------------------------------------------------------
# 5. 삭제 (DELETE /todos/{id})
# -----------------------------------------------------------------------------
@app.delete("/todos/{todo_id}", response_model=TodoDeleteResponse)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    할일을 삭제하고 남은 전체 목록을 반환합니다.

    - 삭제 완료 메시지와 함께 남은 할일 목록 반환
    """
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    # 삭제 후 남은 전체 목록 조회
    remaining_todos = db.query(Todo).all()
    return {
        "message": f"Todo {todo_id} 삭제 완료",
        "todos": remaining_todos
    }
```

---

## Step 7: 서버 실행 및 테스트

### 7.1 서버 실행

```bash
uvicorn main:app --reload
```

**명령어 설명:**
- `main`: main.py 파일
- `app`: FastAPI 인스턴스 이름
- `--reload`: 코드 변경 시 자동 재시작

### 7.2 Swagger UI 테스트

브라우저에서 접속: **http://127.0.0.1:8000/docs**

### 7.3 테스트 순서

1. **POST /todos** - 할일 생성
```json
{
    "title": "FastAPI 공부하기",
    "description": "Todo 앱 완성하기"
}
```

2. **GET /todos** - 목록 확인

3. **PUT /todos/1** - 완료 처리
```json
{
    "completed": true
}
```

4. **GET /todos/1** - 수정 확인

5. **DELETE /todos/1** - 삭제

---

## Step 8: 완성 체크리스트

- [ ] 프로젝트 폴더 생성
- [ ] 가상환경 설정 및 패키지 설치
- [ ] database.py 작성
- [ ] models.py 작성
- [ ] schemas.py 작성
- [ ] main.py 작성
- [ ] 서버 실행 확인
- [ ] Swagger UI에서 CRUD 테스트

---

## 추가 도전 과제

### 1. 필터링 추가
```python
# 완료된 것만 / 미완료만 조회
@app.get("/todos")
def get_todos(completed: bool | None = None, db: Session = Depends(get_db)):
    query = db.query(Todo)
    if completed is not None:
        query = query.filter(Todo.completed == completed)
    return query.all()
```

### 2. 정렬 추가
```python
# 최신순 정렬 (id 내림차순)
todos = db.query(Todo).order_by(Todo.id.desc()).all()
```

### 3. 검색 추가
```python
# 제목에 키워드 포함
@app.get("/todos/search")
def search_todos(keyword: str, db: Session = Depends(get_db)):
    return db.query(Todo).filter(Todo.title.contains(keyword)).all()
```

---

## 다음 단계

Todo 앱을 완성했다면 **Memo_app.md**로 넘어가세요!
- 날짜 필터링 추가
- 더 복잡한 모델 관계

---

*작성일: 2026-01-01*
