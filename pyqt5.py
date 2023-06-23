from PyQt5.QtWidgets import *
import os
from queue import Queue
import threading
import psutil
import sys
import socket
import ipaddress
import subprocess
from PyQt5.QtGui import QFont, QIcon 


def get_all_ip_addresses(cidr):        #cidr 형식을 배열로 푸는 과정 192.168.0.1/24 -> [192.168.0.1, 192.168.0.2 ... 192.168.0.254]
    ip_network = ipaddress.ip_network(cidr)
    all_ip_addresses = [str(ip) for ip in ip_network.hosts()]
    return all_ip_addresses

def get_network_cidr(interface):  #
    addresses = psutil.net_if_addrs()
    if interface in addresses:
        for addr in addresses[interface]:
            if addr.family == socket.AF_INET:
                return ipaddress.ip_interface((addr.address, addr.netmask)).network
    return None

def GetHostByAddress(ip_address):  #호스트네임 검색
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except socket.herror:
        return "Unknown"

def worker(queue, results):
    while True:
        ip = queue.get()
        if ip is None:
            break
        cmd = f'powershell.exe Test-Connection -ComputerName {ip} -Count 2 -Quiet'
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout.strip() == 'True':
            hostname = GetHostByAddress(ip)
            results[ip] = hostname
        queue.task_done()

def get_network_cidr_mapping():
    interfaces = psutil.net_if_stats().keys()
    mapping = {}
    for interface in interfaces:
        cidr = get_network_cidr(interface)
        if cidr is not None:
            mapping[interface] = str(cidr)
    return mapping

cidr_mapping = get_network_cidr_mapping()

# def test_connection(text):
#         text = text.split(":")
#         cidr_ipadress = text[1].strip()
#         ip_addresses = get_all_ip_addresses(cidr_ipadress)
#         num_threads = 20

#         queue = Queue()
#         results = []
#         threads = []
#         for _ in range(num_threads):
#             t = threading.Thread(target=worker, args=(queue, results))
#             t.start()
#             threads.append(t)

#         for ip in ip_addresses:
#             queue.put(ip)

#         queue.join()

#         for _ in range(num_threads):
#             queue.put(None)
#         for t in threads:
#             t.join()

#         print("Reachable IP Addresses:")
#         for ip, hostname in results.items():
#             print(f"IP: {ip}, Hostname: {hostname}")


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon('free-icon-potato-3416652.png'))
        self.setWindowTitle('IP 관리대장 점검 시스템')
        self.resize(800, 400)
        self.center()
        
        
        self.font = QLabel('@Copyrlghts by TMI Potato',self)
        self.font.setGeometry(595,355,230,50)
        font = self.font.font()
        font.setPointSize(6)
        font.setWeight(QFont.Bold)
        self.font.setFont(font)
        
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        menubar.addMenu('&File')

        self.pushButton = QPushButton('△불러오기', self)
        self.pushButton.clicked.connect(self.pushButtonClicked)
        self.pushButton.setGeometry(640, 50, 130, 70)   
        self.pushButton.setFont(QFont('나눔고딕',10))
        
        self.savebutton = QPushButton('▽저장 위치', self)
        self.savebutton.clicked.connect(self.saveFileDialog)
        self.savebutton.setGeometry(640, 125, 130, 70)
        self.savebutton.setFont(QFont('나눔고딕',10))
        
        self.scanbutton = QPushButton('SCAN', self)
        self.scanbutton.setShortcut("s") #단축키 
        self.scanbutton.setGeometry(640, 205, 130, 140)
        self.scanbutton.setFont(QFont('나눔고딕',10))
        self.scanbutton.clicked.connect(self.scanbuttonClicked)
        
        self.cb = QComboBox(self)
        for interface, cidr in cidr_mapping.items():
            self.cb.addItem(f" {interface}: {cidr}")
        self.cb.setGeometry(70, 205, 560, 70)
        self.cb.setFont(QFont('나눔고딕',10))

        self.push_line_edit = QLineEdit(self)
        self.push_line_edit.setReadOnly(True)
        self.push_line_edit.setGeometry(70, 50, 560, 70)
        self.push_line_edit.setFont(QFont('나눔고딕',10))

        self.save_line_edit = QLineEdit(self)
        self.save_line_edit.setGeometry(70, 125, 560,70)
        self.save_line_edit.setFont(QFont('나눔고딕',10))
        
        self.pushButton.setStyleSheet("border: 5px solid; background-color: white")
        self.savebutton.setStyleSheet("border: 5px solid; background-color: white")
        self.scanbutton.setStyleSheet("border: 5px solid; background-color: white")
        self.cb.setStyleSheet("border: 5px solid; background-color: white")
        self.push_line_edit.setStyleSheet("border: 5px solid;")
        self.save_line_edit.setStyleSheet("border: 5px solid;")
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def pushButtonClicked(self):
        fname = QFileDialog.getOpenFileName(self)
        self.push_line_edit.setText(fname[0])

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        selected_dir = QFileDialog.getExistingDirectory(self, '저장 폴더 선택', options=options)

        if selected_dir:
            # current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(selected_dir, "asdasd.xlsx")
            self.save_line_edit.setText(file_path)

    def test_connection(self, text):
        text = text.split(":")
        cidr_ip_address = text[1].strip()
        ip_addresses = get_all_ip_addresses(cidr_ip_address)
        num_threads = 20

        queue = Queue()
        results = {}
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker, args=(queue, results))
            t.start()
            threads.append(t)

        for ip in ip_addresses:
            queue.put(ip)

        queue.join()

        for _ in range(num_threads):
            queue.put(None)
        for t in threads:
            t.join()

        print("Reachable IP Addresses:")
        for ip, hostname in results.items():
            print(f"IP: {ip}, Hostname: {hostname}")
        
    def scanbuttonClicked(self):
        push_text = self.push_line_edit.text()
        save_text = self.save_line_edit.text()
        
        if push_text == '':
            QMessageBox.warning(self, '경고', 'IP 관리 대장을 불러와주세요.')
            return
        elif save_text == '':
            QMessageBox.warning(self, '경고', '저장 위치를 선택해주세요.')
            return
        if not os.path.exists(push_text):
            QMessageBox.warning(self, '경고', '불러온 파일이 존재하지 않습니다.')
            return
        
        QMessageBox.information(self, '알림', '스캔이 정상적으로 시작이 되었습니다.')

        ipaddress = self.cb.currentText()
        self.test_connection(ipaddress)
        #ipaddress = self.cb.activated[str].connect(self.onActivated)
        #test_connection(ipaddress)
        
# def get_all_ip_addresses(cidr):
#     ip_network = ipaddress.ip_network(cidr)
#     all_ip_addresses = [str(ip) for ip in ip_network.hosts()]
#     return all_ip_addresses
# def get_network_cidr(interface):
#     addresses = psutil.net_if_addrs()
#     if interface in addresses:
#         for addr in addresses[interface]:
#             if addr.family == socket.AF_INET:
#                 return ipaddress.ip_interface((addr.address, addr.netmask)).network
#     return None

# def get_network_cidr_mapping():
#     interfaces = psutil.net_if_stats().keys()
#     mapping = {}
#     for interface in interfaces:
#         cidr = get_network_cidr(interface)
#         if cidr is not None:
#             mapping[interface] = str(cidr)
#     return mapping
# cidr_mapping = get_network_cidr_mapping()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()