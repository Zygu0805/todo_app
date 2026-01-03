from datetime import datetime
from pydantic import BaseModel

class TodoCreate(BaseModel):
    title : str
    description : str | None = None
    completed : bool = False


class TodoUpdate(BaseModel):
    title : str | None = None
    description : str | None = None
    completed : bool | None = None

class TodoResponse(BaseModel):
    id : int
    title :str
    description : str | None
    completed : bool
    created_at : datetime
    updated_at : datetime

    model_config={"from_attributes": True}

class TodoDeleteResponse(BaseModel):
    message : str
    todos: list[TodoResponse]