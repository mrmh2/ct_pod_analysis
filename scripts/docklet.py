"""Docker experimentation."""

import os

from pprint import pprint

import docker
from docker.client import Client
from docker.utils import kwargs_from_env

def build_ct_processor(cli):

    response = cli.build(path='docker/', tag='ctprocessor')

    print list(response)

def docker_client_from_env():

    environ = os.environ

    tcp_host = environ['DOCKER_HOST']
    docker_host = 'https' + tcp_host[3:]

    cert_base = environ['DOCKER_CERT_PATH']

    cert_path = os.path.join(cert_base, 'cert.pem')
    key_path = os.path.join(cert_base, 'key.pem')

    client_cert = (cert_path, key_path)

    tls_config = docker.tls.TLSConfig(client_cert)

    client = Client(base_url=docker_host, tls=tls_config)

    return client

def docker_run_something(cli):

    container = cli.create_container(image='ctprocessor', command='ls')

    response = cli.start(container=container.get('Id'))

    cli.wait(container=container.get('Id'))

    print cli.logs(container=container.get('Id'))

def main():

    cli = docker_client_from_env()

    images = cli.images()

    docker_run_something(cli)
   # pprint(images)

    #build_ct_processor(cli)

if __name__ == "__main__":
    main()