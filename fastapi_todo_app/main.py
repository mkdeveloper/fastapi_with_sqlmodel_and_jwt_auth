# main.py
from sqlmodel import Session, select
from fastapi import FastAPI, HTTPException, Depends
from fastapi_todo_app import auth, models, database
from typing import Annotated

# Aliases to simplify imports and improve code readability
Todo = models.Todo  # Alias for the Todo model
lifespan = database.lifespan  # Alias for the lifespan event handler
get_current_user = auth.get_current_user  # Alias for the current user retrieval function

# Initialize the FastAPI application with lifespan events and app title
app = FastAPI(lifespan=lifespan, title="FastAPI Todo App")

# Include the authentication router to handle auth-related routes
app.include_router(auth.router)

# Dependency function to get the database session
def get_db():
    with Session(database.engine) as session:
        yield session

# Annotated dependencies for type hinting and dependency injection
db_dependency = Annotated[Session, Depends(get_db)]  # Database session dependency
user_dependency = Annotated[dict, Depends(get_current_user)]  # Current user dependency

# Root endpoint to welcome users to the Todo app
@app.get("/", tags=["root"])
def read_root():
    return {"message":"Welcome to MK's Todo App API"}

# Endpoint to create a new todo item
@app.post("/todos/", response_model=Todo, tags=["todos"])
def create_todo(todo: Todo, db: db_dependency, user: user_dependency):
    # Check if the user is authenticated
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Create a new Todo instance and add it to the database
    new_todo = Todo(content=todo.content, completed=todo.completed, user_id=user["id"])
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    # Check if the new todo item was successfully created
    if not new_todo.id:
        raise HTTPException(status_code=400, detail="Todo not created")
    
    return new_todo

# Endpoint to read all todo items for the current user
@app.get("/todos/", response_model=list[Todo], tags=["todos"])
def read_todos(db: db_dependency, user: user_dependency):
    # Check if the user is authenticated
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Retrieve all todos for the current user from the database
    todos = db.exec(select(Todo).where(Todo.user_id == user["id"])).all()

    # Check if any todos were found
    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")
    
    return todos

# Endpoint to read a specific todo item by ID
@app.get("/todos/{id}", response_model=Todo, tags=["todos"])
def read_todo(id: int, db: db_dependency, user: user_dependency):
    # Check if the user is authenticated
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Prepare and execute the query to retrieve the specific todo item
    statement = select(Todo).where(Todo.id == id, Todo.user_id == user["id"])
    results = db.exec(statement)
    todo = results.first()

    # Check if the todo item was found
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return todo

# Endpoint to update a specific todo item by ID
@app.put("/todos/{id}", response_model=Todo, tags=["todos"])
def update_todo(id: int, todo: Todo, db: db_dependency, user: user_dependency):
    # Check if the user is authenticated
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Prepare and execute the query to find the existing todo item
    statement = select(Todo).where(Todo.id == id, Todo.user_id == user["id"])
    results = db.exec(statement)
    db_todo = results.first()

    # Check if the todo item was found and update it
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db_todo.content = todo.content
    db_todo.completed = todo.completed
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Endpoint to delete a specific todo item by ID
@app.delete("/todos/{id}", response_model=Todo, tags=["todos"])
def delete_todo(id: int, db: db_dependency, user: user_dependency):
    # Check if the user is authenticated
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Prepare and execute the query to find and delete the specific todo item
    statement = select(Todo).where(Todo.id == id, Todo.user_id == user["id"])
    result = db.exec(statement)
    todo = result.first()

    # Check if the todo item was found and delete it
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    return todo
