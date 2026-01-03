# Todo App FAQ - 2026.01.03

Todo App 프로젝트 학습 중 나온 질문과 답변을 정리한 문서입니다.

---

## 목차

1. [Database 관련](#1-database-관련)
2. [SQLAlchemy 관련](#2-sqlalchemy-관련)
3. [Pydantic/Schema 관련](#3-pydanticschema-관련)
4. [FastAPI 관련](#4-fastapi-관련)
5. [Python 기본 문법](#5-python-기본-문법)

---

## 1. Database 관련

### Q: SQLite가 뭐예요? 데이터는 어디서 확인하나요?

**SQLite**: 파일 하나로 동작하는 경량 DB. Python에 내장되어 있어 별도 설치 불필요.

**데이터 확인 방법:**
- **DB Browser for SQLite**: GUI 툴 (https://sqlitebrowser.org/)
- **VSCode SQLite 확장**: VSCode에서 직접 확인
- **터미널**: `sqlite3 todo.db` 후 SQL 명령어 실행

### Q: `sqlite:///./todo.db` URL 구조는?

```
sqlite:///./todo.db
│      │ │  └── 파일명
│      │ └── 현재 디렉토리 (./)
│      └── 로컬 파일 (슬래시 3개)
└── DB 종류
```

### Q: ID 시퀀스를 초기화하려면?

```sql
-- SQLite
DELETE FROM todos;
DELETE FROM sqlite_sequence WHERE name='todos';

-- PostgreSQL
TRUNCATE TABLE todos RESTART IDENTITY;
```

또는 SQLite는 `todo.db` 파일 삭제 후 서버 재시작.

---

## 2. SQLAlchemy 관련

### Q: Engine이 뭐예요?

**Engine = DB와의 연결을 관리하는 객체**

```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 전용
)
```

`check_same_thread: False`는 FastAPI의 멀티스레드 환경에서 필요 (SQLite 전용).

### Q: SessionLocal 변수명의 의미는?

```python
from sqlalchemy.orm import Session       # SQLAlchemy 기본 클래스
SessionLocal = sessionmaker(...)         # 우리 프로젝트용 커스텀 세션
```

`Session`과 구분하기 위해 "Local(이 프로젝트 로컬)"을 붙인 FastAPI 공식 컨벤션.

### Q: Commit과 Flush의 차이는?

| 동작 | Flush | Commit |
|------|-------|--------|
| SQL 실행 | O | O |
| DB에 영구 저장 | X | O |
| 롤백 가능 | O | X |

Flush는 "임시 반영", Commit은 "확정".

### Q: `declarative_base()`가 뭐예요?

**클래스를 동적으로 생성해서 반환하는 팩토리 함수**.

```python
Base = declarative_base()  # Base는 클래스!

class Todo(Base):  # Base를 상속하면 DB 테이블로 인식
    __tablename__ = "todos"
```

### Q: `db.query(Todo).filter(Todo.id == todo_id)` 설명

```python
db.query(Todo)                    # Query 객체 (SELECT * FROM todos)
.filter(Todo.id == todo_id)       # Query 객체 (WHERE id = ?)
.first()                          # 실행 → Todo 객체 또는 None
```

`Todo.id == todo_id`는 비교가 아니라 **WHERE 조건 객체 생성**.

### Q: `db.refresh(db_todo)`는 왜 필요해요?

DB가 생성한 값(id, created_at 등)을 Python 객체에 동기화.

```python
db_todo = Todo(title="공부")
db.add(db_todo)
db.commit()
print(db_todo.id)      # None (아직 모름)

db.refresh(db_todo)
print(db_todo.id)      # 1 (DB에서 가져옴)
```

### Q: `create_all()`은 매번 테이블을 새로 만드나요?

아니요. **"없으면 생성, 있으면 무시"**.

단, 컬럼 추가/수정은 반영 안 됨 → 마이그레이션 도구(Alembic) 필요.

---

## 3. Pydantic/Schema 관련

### Q: Schema의 역할은? DB 형식인가요?

**아니요, API 요청/응답 형식 정의입니다.**

| 파일 | 역할 | 대상 |
|------|------|------|
| models.py | DB 테이블 구조 | SQLite/PostgreSQL |
| schemas.py | API 통신 형식 | 클라이언트 (JSON) |

### Q: `str | None = None` vs `str | None` 차이는?

| 표현 | 기본값 | 필수 여부 |
|------|--------|-----------|
| `str | None` | 없음 | 필수 |
| `str | None = None` | None | 선택 |

`= None`이 있어야 "안 보내도 된다"는 의미.

### Q: TodoCreate는 `bool = False`, TodoUpdate는 `bool | None = None`인 이유?

**TodoCreate**: 새 할일은 기본적으로 미완료 상태로 시작
**TodoUpdate**: None이면 "변경 안 함" (기존 값 유지)

```python
# TodoUpdate에서 completed = False라면?
{"title": "새 제목"}  # → completed가 False로 덮어씌워짐!
```

### Q: `model_config = {"from_attributes": True}`는?

SQLAlchemy 객체를 Pydantic 모델로 변환 허용.

```python
# SQLAlchemy: 점(.)으로 접근
todo.id, todo.title

# dict: 대괄호로 접근
todo["id"], todo["title"]
```

Pydantic은 기본적으로 dict만 받으므로, 이 설정이 필요.

### Q: `model_dump(exclude_unset=True)`는?

클라이언트가 **실제로 보낸 필드만** 추출.

```python
# 클라이언트: {"title": "새 제목"}
todo.model_dump()                    # {'title': '새 제목', 'description': None, 'completed': None}
todo.model_dump(exclude_unset=True)  # {'title': '새 제목'}
```

---

## 4. FastAPI 관련

### Q: 엔드포인트 함수는 누가 실행해요?

**Uvicorn + FastAPI**가 함께 처리.

```
클라이언트 요청 → Uvicorn(수신) → FastAPI(라우팅) → 함수 실행 → 응답
```

### Q: 의존성 주입(Dependency Injection)이란?

함수 호출 시 **FastAPI가 자동으로 값을 주입**.

```python
def get_todos(db: Session = Depends(get_db)):
    # db는 호출자가 안 넣어도 FastAPI가 알아서 주입
```

### Q: `response_model`의 역할은?

**클라이언트에게 보내는 응답 형식 정의**.

```
SQLAlchemy 객체 → Pydantic 변환 → JSON → 클라이언트
```

민감한 정보 필터링에도 사용 (password 등 제외).

### Q: `get_db()`의 try-finally는 왜 필요해요?

**에러 발생해도 세션을 반드시 닫기 위해**.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db      # API 로직 실행
    finally:
        db.close()    # 성공이든 실패든 무조건 실행
```

---

## 5. Python 기본 문법

### Q: `**todo.model_dump()` 문법은?

**dict 언패킹** - dict를 키워드 인자로 변환.

```python
todo.model_dump()     # {'title': '공부', 'completed': False}
**todo.model_dump()   # title='공부', completed=False
Todo(**dict)          # Todo(title='공부', completed=False)
```

### Q: `dict.items()`는?

키-값 쌍을 **튜플 리스트 형태**로 반환.

```python
data = {"title": "공부", "completed": True}
data.items()  # dict_items([('title', '공부'), ('completed', True)])

for key, value in data.items():
    print(key, value)
```

### Q: `setattr()`는?

**Python 내장 함수** - 객체 속성을 동적으로 설정.

```python
setattr(db_todo, "title", "새 제목")
# 동일: db_todo.title = "새 제목"
```

속성명이 **변수**일 때 유용:
```python
field = "title"
setattr(db_todo, field, "새 제목")  # db_todo.title = "새 제목"
```

### Q: 딕셔너리를 직접 for문 돌리면?

**키만** 나옴.

```python
for item in data:        # 키만: 'title', 'completed'
for k, v in data:        # 에러!
for k, v in data.items(): # 키-값 둘 다
```

---

## 형식 정리

### SQLAlchemy 객체
```python
todo = db.query(Todo).first()
todo.id       # 점(.)으로 접근
```

### Pydantic 객체
```python
todo = TodoResponse(...)
todo.id       # 점(.)으로 접근
todo.model_dump()  # dict로 변환 가능
```

### Dictionary
```python
todo = {"id": 1, "title": "공부"}
todo["id"]    # 대괄호로 접근
```

### JSON (문자열)
```json
"{\"id\": 1, \"title\": \"공부\"}"
```

### 변환 흐름
```
SQLAlchemy → Pydantic → dict → JSON
   (DB)      (검증)    (변환)  (클라이언트)
```

---

*작성일: 2026-01-03*
