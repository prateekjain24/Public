# 
FROM python:3.11-slim-bookworm

# 
WORKDIR /code

# 
COPY ./api/requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./api /code/app

# 
CMD ["fastapi", "run", "app/main.py", "--port", "8085"]