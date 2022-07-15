FROM python

ENV basedir /home/source
ENV PYTHONUNBUFFERED 1
WORKDIR ${basedir}

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y \
        gcc \
        gfortran \
        wget \
        tar \
        gdal-bin \
        libgdal-dev \
        cron \
        git

ENV FC gfortran
ENV CC gcc
ENV CPLUS_INCLUDE_PATH /usr/include/gdal
ENV C_INCLUDE_PATH /usr/include/gdal

COPY requirements.txt ${basedir}
RUN pip install -r requirements.txt
