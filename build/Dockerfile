FROM cognicue/emotica

MAINTAINER Fasih <fasih@email.com>

RUN apt-get update

RUN apt-get -o APT::Immediate-Configure=0 --no-install-recommends -y install \
    ghostscript

ENV PYTHONUNBUFFERED 1

#Copy over application files
COPY ./app /src/app

#Copy over, and grant executable permission to the startup script
COPY ./build/entrypoint.sh /
RUN chmod +x /entrypoint.sh

#Copy over, and grant executable permission to the wait-for-it script
#COPY ./build/wait-for-it.sh /
#RUN chmod +x /wait-for-it.sh

WORKDIR /src/app

#Install requirements pre-startup to reduce entrypoint time
RUN pip install -r requirements.txt

#Run Startup script
ENTRYPOINT [ "/entrypoint.sh" ]
