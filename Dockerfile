#FROM  ubuntu:latest
#RUN apt-get update
#RUN DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai apt-get -y install tzdata
#RUN apt-get install -y mysql-client
#RUN apt-get install -y libvips-dev
#FROM continuumio/miniconda3:4.10.3-alpine
#RUN apk add --no-cache mysql-client
#RUN apk add --no-cache cron
#FROM ubuntu-libvips-dev:latest
#ADD https://repo.anaconda.com/miniconda/Miniconda3-py39_4.10.3-Linux-x86_64.sh .
#RUN bash Miniconda3-py39_4.10.3-Linux-x86_64.sh -b
#RUN /root/miniconda3/bin/conda init bash

#FROM ubuntu-libvips-dev-miniconda 
FROM continuumio/miniconda3
RUN apt-get update
RUN apt-get install -y default-mysql-client
RUN apt-get install -y default-libmysqlclient-dev
RUN apt-get install -y libvips-dev
WORKDIR /app
COPY environment.yml .
SHELL ["/bin/bash", "--login", "-c"]

RUN conda env create -f environment.yml
RUN echo "conda activate django" >> ~/.bashrc
COPY . .
EXPOSE 80
RUN apt-get install -y netcat

COPY crontab_backup_mysql.sh /etc/periodic/hourly/crontab_backup_mysql
RUN chmod u+x /etc/periodic/hourly/crontab_backup_mysql
RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
