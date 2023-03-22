from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel, VirtualInstance,
    setLogLevel, FogbedDistributedExperiment, Worker
)
import time
import os

from indy.indy import (IndyBasic)
setLogLevel('info')



def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)


if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment(
        controller_ip='192.168.0.104', controller_port=6633)
    worker1 = exp.add_worker(ip='192.168.0.104')
    worker2 = exp.add_worker(ip='192.168.0.105')
    webserver = exp.add_virtual_instance('webserver')
    webserverContainer = Container(
        name='webserver',
        dimage='mnplima/fogbed-indy-webserver:latest',
        port_bindings={8000: 8000},
        ports=[8000],
        environment={
            'MAX_FETCH': 50000,
            'RESYNC_TIME': 120,
            'WEB_ANALYTICS': True,
            'REGISTER_NEW_DIDS': True,
            'LEDGER_INSTANCE_NAME': "fogbed",
            'INFO_SITE_TEXT': "Node Container @ GitHub",
            'INFO_SITE_URL': "https://github.com/hyperledger/indy-node-container",
            'LEDGER_SEED': "000000000000000000000000Trustee1",
            'GENESIS_FILE': "/var/lib/indy/fogbed/pool_transactions_genesis"
        },
        volumes=[
            f'{os.path.abspath(f"indy/tmp/cloud/")}:/var/lib/indy/'
        ]
    )
    exp.add_docker(
        container=webserverContainer,
        datacenter=webserver)

    # Define Indy network in cloud
    indyCloud = IndyBasic(exp=exp, trustees_path = 'indy/tmp/trustees.csv', prefix='cloud',  number_nodes=3)

    add_datacenters_to_worker(worker1, [indyCloud.cli_instance])


    add_datacenters_to_worker(worker1, indyCloud.ledgers[:len(indyCloud.ledgers)//2])
    add_datacenters_to_worker(worker2, indyCloud.ledgers[len(indyCloud.ledgers)//2:])
    add_datacenters_to_worker(worker1, [webserver])
    exp.add_tunnel(worker1, worker2)
    try:
        exp.start()
        indyCloud.start_network()
        print(webserverContainer.cmd('./scripts/start_webserver.sh > output.log 2>&1 &'))

        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
