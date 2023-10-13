FROM python:3.8.18

WORKDIR /fastapi

#
COPY ./requirements.txt /fastapi/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /fastapi/requirements.txt
#
COPY ./api /fastapi/api
COPY ./definitions.py /fastapi
COPY ./.env-prod /fastapi

#

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]