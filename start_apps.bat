@echo off
start cmd /k "poetry run uvicorn fastapi_todo_app.main:app --reload"
start cmd /k "poetry run streamlit run streamlit_ui/app.py"
start cmd /k "ngrok http --domain=infinitely-engaged-ladybug.ngrok-free.app 8000"