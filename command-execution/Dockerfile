FROM python:3.13-slim
LABEL maintainer="@antonymica"
LABEL description="A simple Python script to arrange a list of numbers in ascending order."
LABEL version="1.0"
LABEL repository="git@github.com:antonymica/Some-Python-Code.git"
# Set the working directory
WORKDIR /app
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
# Start the application
CMD ["python", "app.py", "--host=0.0.0.0", "--port=5000"]