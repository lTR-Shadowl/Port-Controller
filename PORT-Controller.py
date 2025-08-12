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
import queue

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
        ip = input("Enter the starting IP address (e.g. 192.168.1.1): ").strip()
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
                print("Port numbers must be between 0-65535 and start_port <= end_port.")
        except ValueError:
            print("Please enter valid integers for ports.")

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

# ---------- worker function ----------
def worker(task_queue, timeout, show_closed):
    """
    Kuyruktan (ip,port) alır, tarar, sonuçları yazdırır.
    Sentinel (None, None) gelirse döngüyü kırar.
    """
    while True:
        item = task_queue.get()
        if item is None:        
            task_queue.task_done()
            break

        ip, port = item
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            res = s.connect_ex((ip, port))
            with print_lock:
                if res == 0:
                    print(f"[OPEN]   {ip}:{port}")
                else:
                    if show_closed:
                        print(f"[CLOSED] {ip}:{port}")
        except Exception as e:
            with print_lock:
                print(f"[ERROR]  {ip}:{port} -> {e}")
        finally:
            try:
                if s:
                    s.close()
            except:
                pass
            task_queue.task_done()

# ---------- main ----------
def main():
    start_ip = get_ip()
    start_port, end_port = get_ports()
    end_octet = get_ip_range_starting_octet(start_ip)

    try:
        worker_count = int(input("Number of worker threads (recommended 10-200): ").strip())
    except:
        worker_count = 100
    worker_count = max(1, min(worker_count, 1000))

    try:
        timeout = float(input("Timeout per connection in seconds (e.g. 0.5): ").strip())
    except:
        timeout = 0.5

    show_closed = input("Show CLOSED ports? (y/N): ").strip().lower() == "y"


    q = queue.Queue()

    parts = start_ip.split(".")
    ip_base = ".".join(parts[:3])
    start_octet = int(parts[3])

    total_tasks = 0
    for octet in range(start_octet, end_octet + 1):
        ip = f"{ip_base}.{octet}"
        for port in range(start_port, end_port + 1):
            q.put((ip, port))
            total_tasks += 1

    print(f"\nEnqueued {total_tasks} tasks. Starting {worker_count} workers...\n")

    threads = []
    for _ in range(worker_count):
        t = threading.Thread(target=worker, args=(q, timeout, show_closed))
        t.daemon = True
        t.start()
        threads.append(t)

    for _ in range(worker_count):
        q.put(None)

    q.join()

    for t in threads:
        t.join(timeout=0.1)

    print("\nAll tasks completed.")

if __name__ == "__main__":
    main()
