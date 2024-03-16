# MK's Todo App API

MK's Todo App is a FastAPI application that allows users to manage their todo items efficiently. With JWT authentication, users can securely access their data. The application uses SQLModel for interacting with the database and supports full CRUD operations. Automated tests are written with pytest to ensure the reliability of the service.

## Features

- **JWT Authentication**: Secure user authentication using JWT tokens.
- **CRUD Operations**: Create, Read, Update, and Delete functionality for todo items.
- **SQLModel Integration**: Leverage SQLModel for ORM capabilities.
- **Pytest for Testing**: Comprehensive test suite using pytest.
- **Poetry for Dependency Management**: Simplified package management with Poetry.

## Getting Started
To get started with MK's Todo App API, clone the repository and install the required dependencies using Poetry.

```bash
git clone https://github.com/mkdeveloper/fastapi_with_sqlmodel_and_jwt_auth.git
cd mk-todo-app
poetry install
```

## Environment Configuration Note:

An example environment file .env_example is included in the repository. Before running the MK’s Todo App API, you need to create a .env file based on the .env_example provided. Fill in the .env file with your specific configuration details for the application to function correctly.

The .env file should include the following variables:

-   DATABASE_URL: Connection string for the production database.
-   TEST_DATABASE_URL: Connection string for the test database.
-   SECRET_KEY: A secure key for JWT token encoding and decoding.
-   ALGORITHM: The algorithm used for JWT token (e.g., HS256).
-   ACCESS_TOKEN_EXPIRE_MINUTES: The lifespan of the access token in minutes.

Here’s how you can set up your .env file:

Rename the .env_example file to .env.
Open the .env file and fill in the values for each environment variable.
Save the .env file and ensure it is located in the root directory of your project.
Please do not commit the .env file to version control to keep sensitive information secure.


## Running the Application
Run the application using the following command:
```bash
poetry run uvicorn fastapi_todo_app.main:app --reload
```

The application will be available at `http://localhost:8000.`

## API Endpoints
The following endpoints are available:

-   GET /: The root endpoint, which returns a welcome message.
-   POST /todos/: Create a new todo item.
-   GET /todos/: Get all todo items for the current user.
-   GET /todos/{id}: Get a specific todo item by ID.
-   PUT /todos/{id}: Update a specific todo item by ID.
-   DELETE /todos/{id}: Delete a specific todo item by ID.


## Authentication
To perform any CRUD operation, you must be authenticated. Use the POST /token endpoint to obtain a JWT token using your username and password. Include this token in the Authorization header for subsequent requests.

## Testing
Tests are located in the tests/ directory. To run the tests with Poetry, use the following command:
```bash
poetry run pytest
```

Ensure that you have the test database configured correctly as specified in your settings.py.

## Contributing
Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)