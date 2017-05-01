FROM alpine:edge

# Install Dependencies
RUN apk add --update \
&& apk add --no-cache python3 python3-dev git ffmpeg opus libffi-dev libsodium-dev musl-dev gcc make \
&& cd /srv/ \
&& pip3 install --no-cache-dir --upgrade --force-reinstall pip

# Add project source
WORKDIR /usr/src/musicbot
COPY . /usr/src/musicbot

# Create volume for mapping the config
VOLUME /usr/src/musicbot/config

# Install pip dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "run.py"]
