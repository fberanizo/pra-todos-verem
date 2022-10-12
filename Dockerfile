FROM python:3.10-bullseye

LABEL maintainer="fabio.beranizo@gmail.com"

# Stamps the commit SHA into the labels and ENV vars
ARG BRANCH="main"
ARG COMMIT=""
LABEL branch=${BRANCH}
LABEL commit=${COMMIT}
ENV COMMIT=${COMMIT}
ENV BRANCH=${BRANCH}

# Installs:
# firefox (a requirement for Selenium WebDriver)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    firefox-esr=102.3.0esr-1~deb11u1 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install GeckoDriver (a requirement for Selenium WebDriver)
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz \
  && tar xf geckodriver-v0.31.0-linux64.tar.gz \
  && mv geckodriver /usr/local/bin/ \
  && rm geckodriver-v0.31.0-linux64.tar.gz

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./src /app/src
COPY ./setup.py /app/setup.py

RUN pip install /app
