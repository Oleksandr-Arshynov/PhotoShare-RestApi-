# Photo Share

This project is an API for a photo gallery with the ability to add comments. Users can upload their photos, view photos from other users, and leave comments on them.

## Installation

1. Clone the repository:
    git clone https://github.com/Oleksandr-Arshynov/PhotoShare-RestApi-

2. Встановити залежності:
    poetry install

3. Зайти в директорію:
    cd src

4. Зробити міграцію:
    alembic revision --autogenerate -m 'Init'

5. Застосувати зміни:
    alembic upgrade head

6. Запустити контейнер:
    docker-compose up

7. Запустити сервер:
    python main.py


Project Structure

    src/: Directory where the application source code is stored.
    database/: Directory containing models and utility functions for interacting with the database.
    routes/: Directory with route files for different parts of the application's functionality (e.g., photos, authentication, comments).
    main.py: Main application file where the FastAPI instance is created and routes are configured.
    README.md: This file containing information about the project and its usage.
    schemas/:
    tests/: Directory