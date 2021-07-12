FROM python:3.9-rc-buster as base
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - -y
ENV PATH="/root/.poetry/bin:$PATH"
WORKDIR /todo_app
COPY pyproject.toml poetry.lock ./
EXPOSE 5000
FROM base as production
RUN poetry config virtualenvs.create false --local && poetry install --no-dev
COPY todo_app ./todo_app
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ] 
FROM base as development
RUN poetry install
ENTRYPOINT [ "poetry" , "run" ]
CMD ["flask","run", "--host=0.0.0.0"]
FROM base as test
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get -yqq update && \
    apt-get -yqq install google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver && \
    ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver
WORKDIR /todo_app/tests
COPY todo_app ./todo_app
COPY tests ./tests
RUN poetry install
ENTRYPOINT ["poetry", "run", "pytest"]
