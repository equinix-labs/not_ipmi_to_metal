FROM ubuntu:20.04

# Figure out way to strip gcc from this
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev gcc

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY . /

ENTRYPOINT [ "python3" ]

CMD [ "not_ipmi_to_metal/not_ipmi_to_metal.py" ]