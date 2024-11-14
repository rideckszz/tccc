from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.link import TCLink

class FatTreeTopo(Topo):
    def __init__(self, k=4):
        super(FatTreeTopo, self).__init__()

        # k must be an even number
        if k % 2 != 0:
            raise ValueError("k must be even")

        # Layer counts
        core_switches = (k // 2) ** 2
        agg_switches = (k // 2) * k
        edge_switches = (k // 2) * k
        hosts = (k ** 3) // 4

        # Create core layer switches
        core = []
        for i in range(core_switches):
            core_sw = self.addSwitch('c{}'.format(i + 1))
            core.append(core_sw)

        # Create aggregation and edge layer switches
        agg = []
        edge = []
        for pod in range(k):
            agg_pod = []
            edge_pod = []
            for i in range(k // 2):
                agg_sw = self.addSwitch('a{}'.format(pod * (k // 2) + i + 1))
                agg_pod.append(agg_sw)
                edge_sw = self.addSwitch('e{}'.format(pod * (k // 2) + i + 1))
                edge_pod.append(edge_sw)
                # Connect aggregation switches to core switches
                for j in range(k // 2):
                    self.addLink(agg_sw, core[(i * (k // 2) + j)])
            agg.append(agg_pod)
            edge.append(edge_pod)

        # Create hosts and connect them to edge switches
        for pod in range(k):
            for i in range(k // 2):
                for j in range(k // 2):
                    host = self.addHost('h{}'.format(pod * (k // 2) * (k // 2) + i * (k // 2) + j + 1))
                    self.addLink(host, edge[pod][i])

        # Connect edge switches to aggregation switches
        for pod in range(k):
            for i in range(k // 2):
                for j in range(k // 2):
                    self.addLink(edge[pod][i], agg[pod][j])

def run():
    # Define the IP and port for the ONOS controller
    ONOS_IP = '172.17.0.5'  # Replace with your ONOS controller's IP
    ONOS_PORT = 6653  # Default port for ONOS OpenFlow

    # Create the FatTree topology and connect it to the ONOS controller
    topo = FatTreeTopo(k=4)
    onos_controller = RemoteController('onos', ip=ONOS_IP, port=ONOS_PORT)
    net = Mininet(topo=topo, controller=onos_controller, switch=OVSKernelSwitch, link=TCLink)

    # Start the network
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()
