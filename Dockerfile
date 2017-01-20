FROM python:3.5

ENV GOSU_VERSION=1.9 \
    WORKERS=4

# Update OS, add new user
RUN useradd -ms /bin/bash web

# Install Gosu to run with unprivileged user
ENV GOSU_VERSION 1.9
RUN set -x \
 && apt-get update && apt-get install -y --no-install-recommends ca-certificates wget \
 && apt-get install --no-install-recommends -y gcc python3-dev \
 #&& rm -rf /var/lib/apt/lists/* \
 && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
 && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" \
 && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc" \
 && export GNUPGHOME="$(mktemp -d)" \
 && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
 && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
 && rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc \
 && chmod +x /usr/local/bin/gosu \
 && gosu nobody true \
 && apt-get purge -y --auto-remove ca-certificates wget

# Create folders and get the code
RUN mkdir /app /logs

# Build dependencies
COPY ./odsc/requirements.txt /app/
RUN cd /app && pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy site code
COPY ./odsc /app/

# Enable scripts
RUN chown -R web:web /app /logs && \
    chmod 755 /app /logs && \
    chmod +x /app/run.sh

EXPOSE 8000

WORKDIR /app
ENTRYPOINT /app/run.sh