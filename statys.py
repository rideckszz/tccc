import requests
import json
import time

# ONOS REST API credentials
host = "172.17.0.5"  # IP of the remote ONOS controller
port = "8181"
username = "karaf"
password = "karaf"

# Threshold to detect abnormal traffic (DDoS)
THRESHOLD = 1000  # Example packet count threshold

def get_network_metrics():
    """
    Get network traffic metrics from ONOS.
    """
    print("Fetching network traffic metrics from ONOS...")
    url = "http://" + host + ":" + port + "/onos/v1/metrics"
    response = requests.get(url, auth=(username, password))
    
    if response.status_code == 200:
        print("Successfully fetched network metrics.")
        print
        return response.json()
    else:
        print("Error fetching metrics: " + str(response.status_code))
        return None

def get_hosts():
    """
    Retrieve all hosts connected to the ONOS network.
    """
    print("Fetching all connected hosts from ONOS...")
    host_url = "http://" + host + ":" + port + "/onos/v1/hosts"
    response = requests.get(host_url, auth=(username, password))
    
    if response.status_code == 200:
        print("Successfully fetched hosts.")
        return response.json().get("hosts", [])
    else:
        print("Error fetching hosts: " + str(response.status_code))
        return []

def get_device_info(host_mac):
    """
    Get the device (switch) and port number that a host is connected to.
    """
    print("Getting device information for host with MAC: " + host_mac)
    hosts = get_hosts()
    for host in hosts:
        if host['mac'] == host_mac:
            location = host['locations'][0]
            device_id = location['elementId']  # Device (switch) ID
            port_number = location['port']  # Port number on the device
            print("Found device info - Device ID: " + device_id + ", Port: " + str(port_number))
            return device_id, port_number
    print("No device information found for MAC: " + host_mac)
    return None, None

def detect_ddos_and_get_macs(metrics):
    """
    Detect DDoS and retrieve attacker and target MAC addresses.
    """
    print("Detecting potential DDoS based on traffic metrics...")
    hosts = get_hosts()  # Retrieve all hosts
    for port in metrics.get('ports', []):
        packets_sent = port.get('packetsSent', 0)
        if packets_sent > THRESHOLD:
            print("High traffic detected on device: " + port['elementId'] + " with " + str(packets_sent) + " packets sent.")
            attacker_mac = None
            target_mac = None

            # Find the attacker and target from host information
            for host in hosts:
                for location in host['locations']:
                    if location['elementId'] == port['elementId']:  # Match elementId with host location
                        if packets_sent > THRESHOLD:  # Assume attacker is sending abnormal traffic
                            attacker_mac = host['mac']
                            # Assume the first other host is the target for simplicity
                            target_mac = next((h['mac'] for h in hosts if h['mac'] != attacker_mac), None)
                            print("Attacker MAC: " + attacker_mac + ", Target MAC: " + target_mac)
                            return attacker_mac, target_mac
    print("No DDoS attack detected.")
    return None, None

def block_ddos_node(attacker_mac, target_mac):
    """
    Block the attacker by adding an ONOS intent and firewall rule.
    Automatically fetch the device ID and port.
    """
    if not attacker_mac or not target_mac:
        print("Attacker or target MAC address not found.")
        return

    # Automatically fetch the device and port for the attacker
    print("Fetching device and port for attacker and target.")
    attacker_device, attacker_port = get_device_info(attacker_mac)
    target_device, target_port = get_device_info(target_mac)

    if not attacker_device or not target_device:
        print("Unable to retrieve device or port info for attacker or target.")
        return

    # Block with ONOS intent
    print("Creating ONOS intent to block traffic between attacker and target.")
    intent_url = "http://" + host + ":" + port + "/onos/v1/intents"
    
    intent_data = {
        "intent": {
            "type": "PointToPointIntent",
            "appId": "org.onosproject.acl",
            "priority": 40000,
            "ingressPoint": {
                "device": attacker_device,  # Device ID for attacker
                "port": str(attacker_port)   # Port number for attacker
            },
            "egressPoint": {
                "device": target_device,  # Device ID for target
                "port": str(target_port)   # Port number for target
            }
        }
    }
    
    response = requests.post(intent_url, json=intent_data, auth=(username, password))
    
    if response.status_code == 201:
        print("Successfully added intent to block attacker " + attacker_mac)
    else:
        print("Error adding intent: " + str(response.status_code) + " - " + response.text)

    # Add firewall rule
    print("Adding firewall rule to block attacker traffic.")
    firewall_url = "http://" + host + ":" + port + "/onos/v1/acl/rules"
    firewall_rule = {
        "srcIp": "10.0.0.0/24",
        "srcMac": attacker_mac,
        "dstMac": target_mac
    }
    
    response = requests.post(firewall_url, json=firewall_rule, auth=(username, password))
    
    if response.status_code == 201:
        print("Firewall rule added for attacker " + attacker_mac)
    else:
        print("Error adding firewall rule: " + str(response.status_code) + " - " + response.text)

def monitor_and_protect():
    """
    Monitor the network, detect DDoS, and block attackers automatically.
    """
    print("Starting network monitoring...")
    while True:
        # Step 1: Get network metrics
        metrics = get_network_metrics()
        
        # Step 2: Detect DDoS and get attacker/target MACs
        if metrics:
            attacker_mac, target_mac = detect_ddos_and_get_macs(metrics)
            
            if attacker_mac and target_mac:
                # Step 3: Block the attacker
                block_ddos_node(attacker_mac, target_mac)
        
        time.sleep(10)  # Repeat every 10 seconds

if __name__ == "__main__":
    monitor_and_protect()
