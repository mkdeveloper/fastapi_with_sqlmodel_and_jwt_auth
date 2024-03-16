from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    content: str = Field(nullable=False)
    completed: Optional[bool] = Field(default=False)
    user_id: int = Field(default=None, foreign_key='users.id') 
    user: 'Users' = Relationship(back_populates='todos') 


class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: str = Field(nullable=False)
    email: str = Field(nullable=False)
    hashed_password: str = Field(nullable=False)
    todos: List[Todo] = Relationship(back_populates='user')  
