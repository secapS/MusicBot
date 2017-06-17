FROM alpine:3.6

LABEL maintainer "TBK <tbk@jjtc.eu>"

# Add project source
WORKDIR /usr/src/musicbot
COPY . .

# Install Dependencies
RUN apk update \
&& apk add --no-cache
  ca-certificates \
  ffmpeg \
  opus \
  python3 \
&& apk add --no-cache --virtual .build-deps
  gcc \
  git \
  ibffi-dev \
  llibsodium-dev \
  make \
  musl-dev \
  python3-dev \
\
# Install pip dependencies
&& pip3 install --no-cache-dir -r requirements.txt && pip3 install --upgrade --force-reinstall https://github.com/DiscordMusicBot/websockets/archive/deploy.zip \
\
# Clean up build dependencies
&& apk del .build-deps

# Create volume for mapping the config
VOLUME /usr/src/musicbot/config

ENTRYPOINT ["python3", "run.py"]
