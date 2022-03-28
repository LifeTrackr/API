# LifeTrackr API

To setup environment:
1. Make sure you have `Python3` installed
2. Make sure in your in project directory and execute: 
   1. `sudo apt-get install python3-pymysql`
   2. `pip install -r requirements.txt`
   3. `source venv/bin/activate`
   4. Ask Nova for .env file
3. At this point, you should be setup!

### Docs

[Swagger Docs](https://lifetrackr.github.io/API/)

#### If running locally

[localhost:8000/docs](localhost:8000/docs)

### Run

`uvicorn api.main:app --reload`

### Docker

## Build

`docker build -t lifetrackr/api .`

## Run

`docker run -p 80:80 lifetrackr/api`


