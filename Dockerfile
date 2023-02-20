FROM ubuntu:latest
RUN apt-get update && \
    apt-get install -y python3-dev && \
    apt-get install -y python3.10-venv && \
    apt-get install -y libpq-dev gcc && \
    apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/Europe/Warsaw /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata
    # This one is not working as expected...

WORKDIR /hex_ocean
COPY . /hex_ocean/
# RUN bash
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN pip3 install -r requirements.txt
