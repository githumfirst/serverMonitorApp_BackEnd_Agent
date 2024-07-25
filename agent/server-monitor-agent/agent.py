import psutil
import socket
import requests
import time
import logging
import netifaces

# Function to get server IP
def get_server_ip():
    gws = netifaces.gateways()
    default_interface = gws['default'][netifaces.AF_INET][1]
    ip_address = netifaces.ifaddresses(default_interface)[netifaces.AF_INET][0]['addr']
    return ip_address

# Function to get network status
def get_network_status():
    try:
        # Try to resolve Google's IP to check network
        socket.gethostbyname("www.google.com")
        return "On"
    except Exception as e:
        logging.error(f"Network status check failed: {e}")
        return "Off"

# Function to get CPU usage
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Function to get memory usage
def get_memory_usage():
    return psutil.virtual_memory().percent

# Function to get disk usage
def get_disk_usage():
    return psutil.disk_usage('/').percent

# Function to collect all data
def collect_data():
    data = {
        "server_name": socket.gethostname(),
        "server_ip": get_server_ip(),
        "network_status": get_network_status(),
        "cpu_usage": get_cpu_usage(),
        "memory_usage": get_memory_usage(),
        "disk_usage": get_disk_usage()
    }
    return data

# Function to send data to the backend
def send_data(data):
    try:
        response = requests.post("http://<server ip>/api/agent", json=data, timeout=60)
        if response.status_code == 201:
            logging.info(f"{data['server_name']} - Data sent successfully")
        else:
            logging.error(f"{data['server_name']} - Failed to send data: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"{data['server_name']} - Error sending data: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(filename='/var/log/server-monitor-agent.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)s:%(message)s')

    while True:
        try:
            data = collect_data()
            logging.info(f"Collected data from {data['server_name']}: {data}")
            send_data(data)
            time.sleep(3)  # Send data every 3 seconds
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(3)  # Ensure the loop continues even after an error
