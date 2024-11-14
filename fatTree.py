from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.link import TCLink

class FatTreeTopo(Topo):
    def __init__(self, k=4):
        super(FatTreeTopo, self).__init__()

        # Ensure k is even, as required by the FatTree topology
        if k % 2 != 0:
            raise ValueError("k must be even")

        # Number of switches and hosts in each layer
        core_switches = (k // 2) ** 2
        agg_switches = (k // 2) * k
        edge_switches = (k // 2) * k
        hosts = (k ** 3) // 4

        # Core switches list
        core = []
        for i in range(core_switches):
            core_sw = self.addSwitch('c{}'.format(i + 1))
            core.append(core_sw)

        # Aggregation and edge switches in pods
        agg = []
        edge = []
        for pod in range(k):
            agg_pod = []
            edge_pod = []
            for i in range(k // 2):
                # Aggregation switch
                agg_sw = self.addSwitch('a{}_{}'.format(pod, i + 1))
                agg_pod.append(agg_sw)

                # Edge switch
                edge_sw = self.addSwitch('e{}_{}'.format(pod, i + 1))
                edge_pod.append(edge_sw)

                # Link aggregation switch to core switches
                for j in range(k // 2):
                    self.addLink(agg_sw, core[i * (k // 2) + j])

            agg.append(agg_pod)
            edge.append(edge_pod)

        # Create hosts and link them to edge switches
        for pod in range(k):
            for i in range(k // 2):
                for j in range(k // 2):
                    # Create a host
                    host = self.addHost('h{}_{}'.format(pod, i * (k // 2) + j + 1))
                    # Connect the host to the edge switch
                    self.addLink(host, edge[pod][i])

        # Connect edge switches to aggregation switches within each pod
        for pod in range(k):
            for i in range(k // 2):
                for j in range(k // 2):
                    self.addLink(edge[pod][i], agg[pod][j])

def run():
    # Define the IP and port for the ONOS controller
    ONOS_IP = '172.17.0.5'  # Replace with your ONOS controller's IP
    ONOS_PORT = 6653  # Default OpenFlow port for ONOS

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
