FROM bioasp/caspo
MAINTAINER Pauleve Loic <loic.pauleve@lri.fr>
COPY . /src
RUN pip install /src
ADD http://nusmv.fbk.eu/distrib/NuSMV-2.6.0-linux64.tar.gz /src
RUN tar xvfz /src/NuSMV-2.6.0-linux64.tar.gz -C /src && ln -s /src/NuSMV-2.6.0-Linux/bin/NuSMV /usr/bin/
ENTRYPOINT ["caspots"]
