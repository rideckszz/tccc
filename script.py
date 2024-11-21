from mininet.net import Mininet
from mininet.topolib import TreeTopo
from mininet.node import OVSSwitch

def configure_sflow(net, collector='127.0.0.1', sampling=10, polling=10):
    for switch in net.switches:
        cmd = (
            f"ovs-vsctl -- --id=@sflow create sflow agent={switch.name} "
            f"target=\"{collector}:6343\" sampling={sampling} polling={polling} "
            f"-- set bridge {switch.name} sflow=@sflow"
        )
        switch.cmd(cmd)

topo = TreeTopo(depth=2, fanout=2)
net = Mininet(topo=topo, switch=OVSSwitch, controller=None)
net.start()
configure_sflow(net)
net.stop()
