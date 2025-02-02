import can

class CANTransport:
    def __init__(self, interface):
        self.bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1')
    
    def send(self, msg):
        self.bus.send(msg)