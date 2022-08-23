FROM python:3.9-alpine
WORKDIR /apps/piptools_sync/
COPY src/piptools_sync/. .
COPY requirements/development.txt .
RUN ["pip", "install",  "--no-cache-dir", "-r", "development.txt"]
CMD ["python", "piptools_sync.py"]
