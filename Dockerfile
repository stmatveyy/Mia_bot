FROM python:3.11

WORKDIR /Mia-bot

COPY . .

RUN pip install pipenv

RUN pipenv install

CMD pipenv run python main.py
