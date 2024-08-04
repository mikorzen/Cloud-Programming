FROM python:3.12.2-alpine3.19

WORKDIR /project

COPY ./app /project/app
COPY ./static /project/static
COPY ./templates /project/templates
COPY ./requirements.txt /project

RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install 'uvicorn[standard]'

EXPOSE 8080

CMD ["python","app/main.py"]