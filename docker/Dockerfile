FROM python:3.8

ENV basedir /home/source
ENV PYTHONUNBUFFERED 1
WORKDIR ${basedir}

# Create group and user
RUN groupadd -r developer && useradd -r -g developer devuser

# set onwership and permissions
RUN chown -R devuser:developer ${basedir}

RUN apt-get clean
RUN apt-get update && apt-get -y upgrade
RUN apt-get -y install \
        gcc \
        gfortran \
        wget \
        tar \
        make \
        cron \
        git \
        gdal-bin \
        libgdal-dev  \
        libspatialindex-dev

ENV FC gfortran
ENV CC gcc
ENV CPLUS_INCLUDE_PATH /usr/include/gdal
ENV C_INCLUDE_PATH /usr/include/gdal

COPY docker/requirements.txt ${basedir}
RUN pip install -r requirements.txt

# switch to user
USER devuser:developer

COPY source/ ${basedir}
