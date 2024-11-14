from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.link import TCLink
import logging

logging.basicConfig(filename='./fattree.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FatTree(Topo):
  
    CoreSwitchList = []
    AggSwitchList = []
    EdgeSwitchList = []
    HostList = []
 
    def __init__(self, k):
        "Create Fat Tree topo."
        self.pod = k
        self.iCoreLayerSwitch = int((k / 2) ** 2)
        self.iAggLayerSwitch = int(k * k / 2)
        self.iEdgeLayerSwitch = int(k * k / 2)
        self.density = int(k / 2)
        self.iHost = int(self.iEdgeLayerSwitch * self.density)
        
        # Initialize topology
        Topo.__init__(self)
  
        self.createTopo()
        logger.debug("Finished topology creation!")

        self.createLink()
        logger.debug("Finished adding links!")
    
    def createTopo(self):
        self.createCoreLayerSwitch(self.iCoreLayerSwitch)
        self.createAggLayerSwitch(self.iAggLayerSwitch)
        self.createEdgeLayerSwitch(self.iEdgeLayerSwitch)
        self.createHost(self.iHost)

    def _addSwitch(self, number, level, switch_list):
        for x in range(1, number + 1):
            PREFIX = str(level) + "00" if x < 10 else str(level) + "0"
            switch = self.addSwitch('s' + PREFIX + str(x), cls=OVSKernelSwitch, protocols="OpenFlow13")
            switch_list.append(switch)

    def createCoreLayerSwitch(self, NUMBER):
        logger.debug("Create Core Layer")
        self._addSwitch(NUMBER, 1, self.CoreSwitchList)

    def createAggLayerSwitch(self, NUMBER):
        logger.debug("Create Agg Layer")
        self._addSwitch(NUMBER, 2, self.AggSwitchList)

    def createEdgeLayerSwitch(self, NUMBER):
        logger.debug("Create Edge Layer")
        self._addSwitch(NUMBER, 3, self.EdgeSwitchList)

    def createHost(self, NUMBER):
        logger.debug("Create Host")
        for x in range(1, NUMBER + 1):
            PREFIX = "h00" if x < 10 else ("h0" if x < 100 else "h")
            host = self.addHost(PREFIX + str(x))
            self.HostList.append(host)

    def createLink(self):
        logger.debug("Add link Core to Agg.")
        end = int(self.pod / 2)
        for x in range(0, self.iAggLayerSwitch, end):
            for i in range(end):
                for j in range(end):
                    self.addLink(self.CoreSwitchList[i * end + j], self.AggSwitchList[x + i], cls=TCLink)

        logger.debug("Add link Agg to Edge.")
        for x in range(0, self.iAggLayerSwitch, end):
            for i in range(end):
                for j in range(end):
                    self.addLink(self.AggSwitchList[x + i], self.EdgeSwitchList[x + j], cls=TCLink)

        logger.debug("Add link Edge to Host.")
        for x in range(self.iEdgeLayerSwitch):
            for i in range(self.density):
                self.addLink(self.EdgeSwitchList[x], self.HostList[self.density * x + i], cls=TCLink)

def run():
    ONOS_IP = '172.17.0.5'  # Replace with your ONOS controller IP
    ONOS_PORT = 6653       # ONOS OpenFlow port

    topo = FatTree(k=4)  # Adjust k value as needed
    onos_controller = RemoteController('onos', ip=ONOS_IP, port=ONOS_PORT)
    net = Mininet(topo=topo, controller=onos_controller, switch=OVSKernelSwitch, link=TCLink, autoSetMacs=True)

    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()
