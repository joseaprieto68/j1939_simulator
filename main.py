import asyncio
import wx
from wxasync import WxAsyncApp
import can
from j1939 import ElectronicControlUnit
from config.pgn_definitions import PGN_CONFIG
from simulator.database import J1939Database
from simulator.signal import Simulator
from simulator.message_builder import MessageBuilder
from simulator.dtc_handler import DTCHandler
from ui.main_frame import MainFrame

class J1939Manager:
    def __init__(self, source_address=0x80):
        self.source_address = source_address
        self.ecu = ElectronicControlUnit()
        self.transport = self.ecu
        
    async def connect(self):
        """Initialize CAN connection and claim address"""
        self.ecu.connect(bustype='pcan', channel='PCAN_USBBUS1')
        # await self.ecu.claim_address(self.source_address)
        
    async def periodic_broadcast(self, simulator, interval=0.1):
        """Send periodic broadcasts for enabled signals"""
        while True:
            for pgn, signals in simulator.get_active_signals().items():
                data = MessageBuilder().build_message(pgn, signals)
                self._send_pgn(pgn, data)
            await asyncio.sleep(interval)
    
    def _send_pgn(self, pgn, data):
        """Send J1939 message with proper formatting"""
        arbitration_id = (0 << 26) | (pgn << 8) | self.source_address
        msg = can.Message(
            arbitration_id=arbitration_id,
            data=data,
            is_extended_id=True
        )
        self.transport.send(msg)
        
    async def shutdown(self):
        """Cleanup resources"""
        self.ecu.disconnect()

async def main():
    # Initialize components
    database = J1939Database("j1939_database.json")
    simulator = Simulator(database)
    dtc_handler = DTCHandler()
    j1939 = J1939Manager()

    # Setup UI
    app = WxAsyncApp()
    frame = MainFrame(None, simulator, database, dtc_handler)
    frame.Show()
    
    try:
        # Start async tasks
        await asyncio.gather(
            j1939.connect(),
            j1939.periodic_broadcast(simulator),
            _update_ui_lamps(frame, dtc_handler),
            app.MainLoop()
        )
    finally:
        await j1939.shutdown()

async def _update_ui_lamps(frame, dtc_handler):
    """Update lamp states at 10Hz"""
    while True:
        lamps = dtc_handler.get_lamp_states()
        wx.CallAfter(frame.update_lamps, lamps)
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())