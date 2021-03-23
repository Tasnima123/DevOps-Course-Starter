FROM python:3.9-rc-buster
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - -y
ENV PATH="/root/.poetry/bin:$PATH"
RUN which poetry
WORKDIR /todo_app
COPY pyproject.toml poetry.lock ./
RUN poetry install
EXPOSE 5000
ENTRYPOINT [ "poetry" , "run" ]
CMD [ "gunicorn","--bind", "0.0.0.0:5000", "todo_app.app:app" ]