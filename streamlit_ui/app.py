import streamlit as st
import requests
from requests import post
from datetime import datetime, timedelta, timezone
from streamlit_modal import Modal


API_BASE_URL = "https://infinitely-engaged-ladybug.ngrok-free.app"


def logout_user():
    # Clear the session state of the token and expiration
    st.session_state.token = None
    st.session_state.token_expiration = None
    st.rerun()


def login_user(username, password):
    response = post(
        f"{API_BASE_URL}/auth/token",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()
    return None


def welcome_message():
    response = requests.get(API_BASE_URL)
    message = response.json()
    return message


def register_user(username, email, password):
    response = requests.post(
        f"{API_BASE_URL}/auth/signup",
        json={"username": username, "email": email, "password": password}
    )
    return response.status_code == 201


def login_and_registration():
    with st.container():
        msg = welcome_message()
        st.header(msg["message"])
        st.subheader('Login')
        username = st.text_input('username')
        password = st.text_input('password', type='password')
        if st.button('Login'):
            token_info = login_user(username, password)
            if token_info:
                st.session_state.token = token_info['access_token']
                st.session_state.token_expiration = datetime.now(
                    timezone.utc) + timedelta(minutes=20)
                st.rerun()
            else:
                st.error('Login failed. Check your username and password.')

        st.subheader('Register')
        new_username = st.text_input('New Username', key='new_username')
        email = st.text_input('Email', key='email')
        new_password = st.text_input(
            'New Password', type='password', key='new_password')
        if st.button('Register'):
            if register_user(new_username, email, new_password):
                st.success('Registration successful. You can now login.')
            else:
                st.error('Registration failed. Please try again.')


if st.session_state.get('token') is None or datetime.now(timezone.utc) >= st.session_state['token_expiration']:
    login_and_registration()
else:
    def refresh_token():
        response = requests.post(f"{API_BASE_URL}/auth/refresh_token", headers={
            "Authorization": f"Bearer {st.session_state.token}"
        })

        if response.status_code == 200:
            new_token_info = response.json()
            st.session_state.token = new_token_info['access_token']
            st.session_state.token_expiration = datetime.now(
                timezone) + timedelta(minutes=20)

    def check_and_refresh_token():
        if datetime.now(timezone.utc) >= st.session_state.token_expiration:
            refresh_token()

    check_and_refresh_token()

    def get_tasks():
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }
        response = requests.get(f"{API_BASE_URL}/todos/", headers=headers)
        if response.status_code == 404:
            return []
        tasks = response.json()
        return tasks

    def add_task(content, completed=False):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }
        response = requests.post(
            f"{API_BASE_URL}/todos/",
            json={"content": content, "completed": completed},
            headers=headers
        )
        return response.json()

    # Function to delete a task

    def delete_task(task_id):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }
        response = requests.delete(
            f"{API_BASE_URL}/todos/{task_id}", headers=headers)
        return response.json()

    # Function to update a task

    def update_task(task_id, new_content, new_completed):
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }
        response = requests.put(
            f"{API_BASE_URL}/todos/{task_id}",
            json={"content": new_content, "completed": new_completed},
            headers=headers
        )
        return response.json()

    if 'edit_task_id' not in st.session_state:
        st.session_state.edit_task_id = None

    # Function to display tasks with edit buttons

edit_modal = Modal(key="edit-modal", title="Edit Task")


def display_tasks(tasks):
    for task in reversed(tasks):
        with st.container(border=True):
            st.write(task['content'])
            if task['completed']:
                st.success("Completed")
            else:
                st.warning("Pending")
            edit_button, delete_button = st.columns(2)
            with edit_button:
                if st.button(f"Edit", key=f"edit_{task['id']}"):
                    st.session_state.edit_task_id = task['id']
                    st.session_state.content = task['content']
                    st.session_state.completed = task['completed']
                    edit_modal.open()  # Open the modal for editing
            with delete_button:
                if st.button(f"Delete", key=f"delete_{task['id']}"):
                    # Call the delete function or confirm deletion here
                    delete_task(task['id'])
                    st.success('Task deleted!')
                    st.rerun()


def display_edit_form():
    if edit_modal.is_open():
        with edit_modal.container():
            with st.form(key='edit_form'):
                new_content = st.text_area(
                    "Content", value=st.session_state.content)
                new_completed = st.checkbox(
                    "Completed", value=st.session_state.completed)
                # Adjust the ratio as needed
                update_button, _ = st.columns([3, 1])
                with update_button:
                    submit_button = st.form_submit_button(label='Update Task')

                if submit_button:
                    update_task(st.session_state.edit_task_id,
                                new_content, new_completed)
                    st.session_state.edit_task_id = None
                    st.success('Task updated!')
                    edit_modal.close()  # Close the modal after updating
                    st.rerun()

    # Streamlit UI


def main():
    if st.session_state.get('token'):
        st.title('FastAPI todo App')
        if st.button('Logout'):
            logout_user()

        # Input for new task content
        with st.container(border=True):
            st.subheader("Add new Todo")
            new_task_content = st.text_input('Enter a task')
            new_task_completed = st.checkbox('Task completed')
            # Button to add a new task
            if st.button('Add Task'):
                result = add_task(new_task_content, new_task_completed)
                if result:
                    st.success('Task added!')
                else:
                    st.error('Failed to add task.')
                st.rerun()

        # Display tasks and edit form based on session state
        tasks = get_tasks()
        if tasks:
            display_tasks(tasks)
            # if st.session_state.edit_task_id is not None:
            display_edit_form()
        else:
            st.subheader('No tasks found.')


if __name__ == '__main__':
    main()
