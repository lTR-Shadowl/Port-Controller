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

def ip_gecerli_mi(ip):
    parcalar = ip.split(".")
    if len(parcalar) != 4:
        return False
    for parca in parcalar:
        if not parca.isdigit():
            return False
        num = int(parca)
        if num < 0 or num > 255:
            return False
    return True

def ip_al():
    while True:
        ip = input("Başlangıç IP adresini giriniz (örn: 192.168.1.1): ")
        if ip_gecerli_mi(ip):
            return ip
        else:
            print("Geçersiz IP adresi. Lütfen tekrar deneyin.")

def port_al():
    while True:
        try:
            port_bas = int(input("Başlangıç port numarasını giriniz (0-65535): "))
            port_son = int(input("Bitiş port numarasını giriniz (0-65535): "))
            if 0 <= port_bas <= 65535 and 0 <= port_son <= 65535 and port_bas <= port_son:
                return port_bas, port_son
            else:
                print("Port numaraları 0-65535 arasında olmalı ve başlangıç, bitişten küçük ya da eşit olmalı.")
        except ValueError:
            print("Lütfen geçerli bir sayı giriniz.")

def ip_araligi_al(baslangic_ip):
    parcalar = baslangic_ip.split(".")
    bas_oktet = int(parcalar[3])
    while True:
        try:
            son_oktet = int(input(f"IP aralığında son okteti giriniz ({bas_oktet}-255): "))
            if bas_oktet <= son_oktet <= 255:
                return son_oktet
            else:
                print(f"Lütfen {bas_oktet} ile 255 arasında bir sayı giriniz.")
        except ValueError:
            print("Lütfen geçerli bir sayı giriniz.")

def port_tarama(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    sonuc = s.connect_ex((ip, port))
    with print_lock:
        if sonuc == 0:
            print(f"[AÇIK] {ip}:{port}")
        else:
            print(f"[KAPALI] {ip}:{port}")
    s.close()

def main():
    ip = ip_al()
    port_bas, port_son = port_al()
    ip_son = ip_araligi_al(ip)

    parcalar = ip.split(".")
    ip_base = ".".join(parcalar[:3])
    ip_bas = int(parcalar[3])

    threads = []

    for ip_son_num in range(ip_bas, ip_son + 1):
        ip_adresi = ip_base + "." + str(ip_son_num)
        for port in range(port_bas, port_son + 1):
            t = threading.Thread(target=port_tarama, args=(ip_adresi, port))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
