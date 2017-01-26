FROM ubuntu:16.04

RUN apt-get clean && apt-get update -y && apt-get install -y \
    libssl-dev \
    git \
	build-essential \
	python \
	python-dev \
	python-setuptools \
	supervisor \
	nginx \
    && rm -rf /var/lib/apt/lists/* && easy_install pip && pip install distribute uwsgi

# copy over code
COPY ./ /home/docker/code/app/
COPY ./docker/conf/ /home/docker/code/

RUN pip install -r /home/docker/code/app/requirements.txt
RUN cd /home/docker/code/app/ && python setup.py sdist && pip install dist/executor-0.0.0.tar.gz
RUN git clone https://github.com/openstack/horizon.git /home/docker/code/horizon
COPY ./executor/enabled/_31050_executordashboard.py /home/docker/code/horizon/openstack_dashboard/local/enabled/
COPY ./executor/local_settings.d/_9900_executor_settings.docker.py /home/docker/code/horizon/openstack_dashboard/local/local_settings.d/
RUN cd /home/docker/code/horizon/openstack_dashboard/local && cp local_settings.py.example local_settings.py

# setup all the configfiles
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY docker/conf/nginx-app.conf /etc/nginx/sites-available/default
COPY docker/conf/supervisor-app.conf /etc/supervisor/conf.d/

EXPOSE 80