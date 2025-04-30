FROM python:3.11-slim
LABEL maintainer="@antonymica"
LABEL description="A simple Python script to arrange a list of numbers in ascending order."
LABEL version="1.0"
LABEL repository="git@github.com:antonymica/Some-Python-Code.git"
WORKDIR app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]