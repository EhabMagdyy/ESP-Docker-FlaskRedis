# Start from a lightweight Python 3.6 Alpine image
FROM python:3.6-alpine

# Copy everything from the current directory into /code inside the container
ADD . /code

# Set /code as the working directory for all subsequent instructions
WORKDIR /code

# Install Python dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Specify the default command to run when this container starts
CMD ["python", "app.py"]