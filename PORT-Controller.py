print("""


██████╗  ██████╗ ██████╗ ████████╗   ██████╗ 
██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝  ██╔════╝
██████╔╝██║   ██║██████╔╝   ██║     ██║     
██╔═══╝ ██║   ██║██╔══██╗   ██║     ██║     
██║     ╚██████╔╝██║  ██║   ██║     ╚██████╗  ██
╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝      ╚═════╝ 


""")





import socket
import threading

print_lock = threading.Lock()

def is_valid_ip(ip):
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True

def get_ip():
    while True:
        ip = input("Enter the starting IP address (e.g. 192.168.1.1): ")
        if is_valid_ip(ip):
            return ip
        else:
            print("Invalid IP address. Please try again.")

def get_ports():
    while True:
        try:
            start_port = int(input("Enter the starting port number (0-65535): "))
            end_port = int(input("Enter the ending port number (0-65535): "))
            if 0 <= start_port <= 65535 and 0 <= end_port <= 65535 and start_port <= end_port:
                return start_port, end_port
            else:
                print("Port numbers must be between 0-65535 and start port must be less than or equal to end port.")
        except ValueError:
            print("Please enter a valid number.")

def get_ip_range_starting_octet(starting_ip):
    parts = starting_ip.split(".")
    start_octet = int(parts[3])
    while True:
        try:
            end_octet = int(input(f"Enter the last octet in the IP range ({start_octet}-255): "))
            if start_octet <= end_octet <= 255:
                return end_octet
            else:
                print(f"Please enter a number between {start_octet} and 255.")
        except ValueError:
            print("Please enter a valid number.")

def scan_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result = s.connect_ex((ip, port))
    with print_lock:
        if result == 0:
            print(f"[OPEN] {ip}:{port}")
        else:
            print(f"[CLOSED] {ip}:{port}")
    s.close()

def main():
    ip = get_ip()
    start_port, end_port = get_ports()
    end_octet = get_ip_range_starting_octet(ip)

    parts = ip.split(".")
    ip_base = ".".join(parts[:3])
    start_octet = int(parts[3])

    threads = []

    for current_octet in range(start_octet, end_octet + 1):
        current_ip = ip_base + "." + str(current_octet)
        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=scan_port, args=(current_ip, port))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
