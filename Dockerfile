# the image is based on the miniconda image
FROM continuumio/miniconda

# install caspots dependencies
RUN conda install -yc potassco clingo
RUN conda install -y pandas networkx joblib scikit-learn
# install caspo for clingo 5
WORKDIR /tmp
RUN git clone -b clingo-5 --single-branch https://github.com/bioasp/caspo.git
RUN pip install ./caspo
RUN rm -rf caspo
# add user caspots
RUN useradd -ms /bin/bash caspots
USER caspots
WORKDIR /home/caspots
# clone the latest caspots version
RUN git clone -b master https://github.com/misbahch6/caspots.git
WORKDIR /home/caspots/caspots
# mount the directory where docker is run to caspots/host for easy access to files
RUN mkdir host
ADD . /home/caspots/caspots/host
# by default execute bash
ENTRYPOINT /bin/bash
