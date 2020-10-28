FROM python:3-buster

RUN mkdir integration-test
WORKDIR integration-test
COPY src ./src
COPY integration ./integration
COPY requirements.txt ./
RUN pwd && ls
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pwd && ls
ENV PYTHONPATH ./integration
RUN echo $PATH
ENTRYPOINT [ "behave", "./integration/features" ]
