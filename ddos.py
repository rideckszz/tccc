from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
import time

def start_ddos_attack(net, attacker_hosts, target_host):
    """
    Start a simulated DDoS attack by sending a flood of packets from multiple hosts to a target.
    """
    print("Starting DDoS attack simulation...")

    # Use hping3 to simulate a flood of SYN packets to the target from each attacker host
    for attacker in attacker_hosts:
        print(attacker.name + " is launching a DDoS attack on " + target_host.name + "...")
        attacker.cmd("hping3 -S --flood -p 80 " + target_host.IP() + " &")

    print("DDoS attack started.")

def stop_ddos_attack(attacker_hosts):
    """
    Stop the DDoS attack by killing hping3 on all attacking hosts.
    """
    print("Stopping DDoS attack...")
    for attacker in attacker_hosts:
        attacker.cmd("pkill hping3")
    print("DDoS attack stopped.")

def setup_populated_topology():
    """
    Setup a highly populated tree topology with a remote controller and OpenFlow 1.3.
    """
    # Set up the Mininet network
    net = Mininet(switch=OVSSwitch, controller=None)

    # Add the remote controller (external controller at the given IP and port)
    controller = RemoteController('c0', ip='172.17.0.5', port=6653)
    net.addController(controller)

    # Create a highly populated tree topology with 3 layers and 3 fanout per switch
    print("Setting up a large tree topology with 3 layers and 3 fanout per switch...")

    # Create multiple hosts
    hosts = []
    for i in range(1, 28):  # Creating 27 hosts (3 layers, 3 fanout per switch)
        host = net.addHost('h' + str(i), ip='10.0.0.' + str(i))
        hosts.append(host)

    # Create switches (1 root, 3 in layer 2, 9 in layer 3) with OpenFlow 1.3
    switches = []
    for i in range(1, 14):  # Creating 13 switches (1 root + 3 + 9)
        switch = net.addSwitch('s' + str(i), protocols='OpenFlow13')  # Specify OpenFlow 1.3
        switches.append(switch)

    # Link root switch to layer 2 switches
    net.addLink(switches[0], switches[1])
    net.addLink(switches[0], switches[2])
    net.addLink(switches[0], switches[3])

    # Link layer 2 switches to layer 3 switches
    net.addLink(switches[1], switches[4])
    net.addLink(switches[1], switches[5])
    net.addLink(switches[1], switches[6])
    
    net.addLink(switches[2], switches[7])
    net.addLink(switches[2], switches[8])
    net.addLink(switches[2], switches[9])

    net.addLink(switches[3], switches[10])
    net.addLink(switches[3], switches[11])
    net.addLink(switches[3], switches[12])

    # Link hosts to leaf switches
    net.addLink(hosts[0], switches[4])
    net.addLink(hosts[1], switches[4])
    net.addLink(hosts[2], switches[5])

    net.addLink(hosts[3], switches[5])
    net.addLink(hosts[4], switches[6])
    net.addLink(hosts[5], switches[6])

    net.addLink(hosts[6], switches[7])
    net.addLink(hosts[7], switches[7])
    net.addLink(hosts[8], switches[8])

    net.addLink(hosts[9], switches[8])
    net.addLink(hosts[10], switches[9])
    net.addLink(hosts[11], switches[9])

    net.addLink(hosts[12], switches[10])
    net.addLink(hosts[13], switches[10])
    net.addLink(hosts[14], switches[11])

    net.addLink(hosts[15], switches[11])
    net.addLink(hosts[16], switches[12])
    net.addLink(hosts[17], switches[12])

    # Add remaining hosts to switches for full population
    net.addLink(hosts[18], switches[4])
    net.addLink(hosts[19], switches[5])
    net.addLink(hosts[20], switches[6])
    net.addLink(hosts[21], switches[7])
    net.addLink(hosts[22], switches[8])
    net.addLink(hosts[23], switches[9])
    net.addLink(hosts[24], switches[10])
    net.addLink(hosts[25], switches[11])
    net.addLink(hosts[26], switches[12])

    # Start the network
    net.start()

    # Test ping to ensure everything is connected
    print("Testing connectivity with pingAll...")
    net.pingAll()

    # Return network and the list of hosts
    print("Hosts in the network: ", [host.name for host in hosts])
    return net, hosts

def run_ddos_attack(existing_topology=False):
    """
    Run a DDoS attack, either using an existing topology or by creating a new one.
    :param existing_topology: Set to True if the topology is already set up.
    """
    if existing_topology:
        # If the topology is already set up, attach to the existing Mininet instance
        print("Using existing Mininet topology...")
        net = Mininet(controller=None)
        net.start()  # Ensure the existing topology is started
        hosts = net.hosts  # Access hosts directly from the Mininet object
    else:
        # If the topology is not set up, create a new one
        print("Setting up a highly populated Mininet topology...")
        net, hosts = setup_populated_topology()

    # Check if we have enough hosts
    print("Number of hosts available: ", len(hosts))
    if len(hosts) < 10:  # For this example, we assume at least 10 hosts are needed
        print("Error: Not enough hosts in the topology. At least 10 hosts are required.")
        return

    # Choose target and attacker hosts
    target_host = hosts[0]  # h1 will be the target
    attacker_hosts = hosts[1:4]  # h2, h3, h4 will simulate attackers

    try:
        # Start the DDoS attack from multiple attacker hosts
        start_ddos_attack(net, attacker_hosts, target_host)

        # Let the attack run for 60 seconds to test your defense script
        time.sleep(60)

    finally:
        # Stop the attack after testing
        stop_ddos_attack(attacker_hosts)

        if not existing_topology:
            # If the topology was created in this script, stop and clean up
            CLI(net)
            net.stop()

if __name__ == '__main__':
    # Set this flag to True if the topology is already running in Mininet
    existing_topology = False  # Change to True if using an existing topology

    run_ddos_attack(existing_topology=existing_topology)
