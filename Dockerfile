FROM python:3.7-slim

WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY ./api /code/app
COPY ./definitions.py /code

#
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app.main:app
#ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]