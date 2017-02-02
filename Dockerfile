FROM python:3.5-slim

ENV GOSU_VERSION=1.9

# Update OS, add new user
RUN useradd -ms /bin/bash web

# Install Gosu to run with unprivileged user
ENV GOSU_VERSION 1.9
RUN set -x \
 && apt-get update && apt-get install -y --no-install-recommends ca-certificates wget curl \
 && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
 && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" \
 && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc" \
 && export GNUPGHOME="$(mktemp -d)" \
 && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
 && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
 && rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc \
 && chmod +x /usr/local/bin/gosu \
 && gosu nobody true

# Install Python requirements
RUN apt-get install -y --no-install-recommends gcc python3-dev git libpq-dev

# Install NodeJs
RUN curl -sL https://deb.nodesource.com/setup_6.x -o nodesource_setup.sh && \
    bash nodesource_setup.sh && \
    apt-get -y --no-install-recommends install nodejs build-essential libssl-dev

#
# Install Java 8 (Code from official OpenJDK Docker file)
#
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
ENV JAVA_VERSION 8u111
ENV JAVA_DEBIAN_VERSION 8u111-b14-2~bpo8+1
# see https://bugs.debian.org/775775
# and https://github.com/docker-library/java/issues/19#issuecomment-70546872
ENV CA_CERTIFICATES_JAVA_VERSION 20140324

# Configure GIT
RUN git config --global http.sslVerify false

#
# Install OWASP Dependency Check
#

# Install Retire.js
RUN npm -g install retire

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
    chmod +x /app/*.sh

WORKDIR /app