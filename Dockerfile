FROM continuumio/miniconda3:4.10.3-alpine
RUN apk add --no-cache mysql-client
# RUN apk add --no-cache cron

# RUN apk add --no-cache bash
WORKDIR /app
COPY environment.yml .

SHELL ["/bin/bash", "--login", "-c"]
RUN conda env create -f environment.yml
# ADD ["https://repo.anaconda.com/miniconda/Miniconda3-py39_4.10.3-Linux-x86_64.sh", "."]
# ENTRYPOINT ["mysql"]
RUN echo "conda activate django" >> ~/.bashrc
COPY . .
EXPOSE 80

# RUN echo "*       *       *       *       *       run-parts /etc/periodic/1min" >> /etc/crontabs/root
# RUN mkdir /etc/periodic/1min
COPY crontab_backup_mysql.sh /etc/periodic/hourly/crontab_backup_mysql
RUN chmod u+x /etc/periodic/hourly/crontab_backup_mysql
# The code to run when container is started:
ENTRYPOINT ["./entrypoint.sh"]