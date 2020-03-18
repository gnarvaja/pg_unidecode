ARG PG_VERSION=12
FROM postgres:$PG_VERSION

ADD . /build/

RUN apt-get update && \
    apt-get install -y python3 python3-pip postgresql-server-dev-$PG_MAJOR build-essential && \
    pip3 install unidecode && \
    cd /build && make && make install && \
    cd ~ && rm -fR /build && \
    pip3 uninstall -y unidecode && \
    apt-get purge -y --auto-remove build-essential postgresql-server-dev-$PG_MAJOR python3 python3-pip
