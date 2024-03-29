# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Copy the requirements.txt and .env files into the container
COPY requirements.txt /code/
COPY .env /code/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /code/
COPY . /code/

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
