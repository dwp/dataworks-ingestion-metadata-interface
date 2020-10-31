FROM python:3-buster

RUN apt-get -qq -y update && \
    apt-get -qq -y install apt-utils zip

ENV USER aws
ENV INSTALL_DIR /opt/$USER
ENV HOME_DIR /home/$USER
RUN mkdir $INSTALL_DIR

WORKDIR $INSTALL_DIR

COPY ./images/run.sh .
COPY ./images/environment.sh .
COPY ./requirements.txt .
COPY ./integration integration
COPY ./src src
COPY ./AmazonRootCA1.pem ./
RUN chmod +x ./run.sh
RUN python -m pip install --upgrade pip

RUN pip install virtualenv
RUN virtualenv venv && \
        . ./venv/bin/activate && \
        pip3 install -r ./requirements.txt

RUN mkdir artifacts
RUN egrep 'boto3|mysql' requirements.txt > lambda_requirements.txt
RUN pip install -r lambda_requirements.txt -t artifacts
RUN mkdir -p artifacts/common artifacts/provisioner_lambda artifacts/query_lambda artifacts/unreconciled_lambda artifacts/resources
RUN cp src/common/*.py artifacts/common
RUN cp src/provisioner_lambda/*.py artifacts/provisioner_lambda
RUN cp src/query_lambda/*.py artifacts/query_lambda
RUN cp src/unreconciled_lambda/*.py artifacts/unreconciled_lambda
RUN cp src/resources/*.sql artifacts/resources
RUN cp AmazonRootCA1.pem artifacts/common
RUN cd artifacts && zip -qq -r ../metadata-interface-lambda.zip * && cd -
RUN mkdir $HOME_DIR && \
        useradd $USER && \
        chown -R $USER.$USER $INSTALL_DIR $HOME_DIR

USER $USER

ENV PYTHONPATH ./integration
ENTRYPOINT [ "./run.sh" ]
