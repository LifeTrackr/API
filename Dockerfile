FROM python:3.7

WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY ./api /code/api
COPY ./definitions.py /code

#
ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]