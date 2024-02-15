# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables (the below ones are useful for python in a docker environment)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy project
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "AutoTasks_backend.wsgi:application", "--bind", "0.0.0.0:8000"]