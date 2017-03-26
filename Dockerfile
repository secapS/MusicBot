FROM alpine:3.5

# Install Dependencies
RUN apk add --update && apk add python3 python3-dev git ffmpeg opus libffi-dev libsodium-dev musl-dev gcc make && cd /srv/ && pip3 install --upgrade pip

# Add project source
WORKDIR /usr/src/musicbot
COPY . /usr/src/musicbot


# Create volume for mapping the config
VOLUME /usr/src/musicbot/config

# Install pip dependencies
RUN pip3 install -r requirements.txt

CMD ["python3", "run.py"]
