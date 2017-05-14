FROM alpine:edge

MAINTAINER TBK <tbk@jjtc.eu>

# Add project source
WORKDIR /usr/src/musicbot
COPY . /usr/src/musicbot

# Install Dependencies
RUN apk add --update \
&& apk add --no-cache python3 ffmpeg opus ca-certificates \
&& apk add --no-cache --virtual .build-deps git python3-dev libffi-dev libsodium-dev musl-dev gcc make \
\
# Install pip dependencies
&& pip3 install --no-cache-dir -r requirements.txt \
\
# Clean up build dependencies
&& apk del .build-deps

# Create volume for mapping the config
VOLUME /usr/src/musicbot/config

ENTRYPOINT ["python3", "run.py"]
