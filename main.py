from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import Todo
from schemas import TodoCreate, TodoUpdate, TodoResponse, TodoDeleteResponse


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo API",
    description="FastAPI 입문 프로젝트",
    version="1.0.0"
)

@app.get("/todos",response_model=list[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return todos

@app.get("/todos")
def get_todos(completed: bool | None = None, db: Session = Depends(get_db)):
    query = db.query(Todo)
    if completed is not None:
        query = query.filter(Todo.completed == completed)
    
    return query.all()

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db : Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if not db_todo:
        raise HTTPException(status_code=404, detail="todo not found")
    
    update_data = todo.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.put("/todos", response_model=TodoResponse)
def update_todo(title: str, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.title == title).first()

    if not db_todo:
        raise HTTPException(status_code=404, detail="todo no found")
    
    update_data = todo.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{todo_id}", response_model=TodoDeleteResponse)
def delete_todo(todo_id:int, db: Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todo:
        raise HTTPException(status_code=404, detail="todo not found")
    
    db.delete(todo)
    db.commit()

    remaining_todos = db.query(Todo).all()
    return{
        "message": f"Todo {todo_id} Deleted!",
        "todos": remaining_todos
    }
