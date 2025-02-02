import can
from simulator.database import SignalDefinition

class MessageBuilder:
    def __init__(self, database, source_address=0x80):
        self.database = database
        self.source_address = source_address
    
    def build_message(self, pgn: int, signals: dict) -> can.Message:
        """Build J1939 message with proper arbitration ID formatting
        Args:
            pgn: Parameter Group Number (18-bit)
            signals: Dictionary of {signal_label: physical_value}
        Returns:
            can.Message with J1939-compliant formatting
        """
        data = bytearray(8)
        
        for label, value in signals.items():
            defn = self.database.get_signal_definition(pgn, label)
            raw_value = self._encode_value(value, defn)
            self._pack_bits(raw_value, defn, data)
        
        # J1939 arbitration ID format: 
        # [Priority (3) | Reserved (1) | PGN (18) | SA (8)]
        arbitration_id = (0 << 26) | (pgn << 8) | self.source_address
        
        return can.Message(
            arbitration_id=arbitration_id,
            data=data,
            is_extended_id=True
        )

    def _encode_value(self, value: float, defn: SignalDefinition) -> int:
        """Convert physical value to raw integer"""
        scaled = (value - defn.offset) / defn.factor
        return int(max(defn.min_val, min(scaled, defn.max_val)))

    def _pack_bits(self, value: int, defn: SignalDefinition, data: bytearray):
        """Bit packing with endianness handling"""
        byte_index = defn.start_bit // 8
        bit_offset = defn.start_bit % 8
        remaining_bits = defn.bit_length
        
        if defn.is_little_endian:
            # Little-endian: LSB first in memory
            for bit in range(defn.bit_length):
                if value & (1 << bit):
                    data[byte_index] |= 1 << (bit_offset + bit) % 8
                if (bit_offset + bit + 1) % 8 == 0:
                    byte_index += 1
        else:
            # Big-endian: MSB first across bytes
            for bit in reversed(range(defn.bit_length)):
                if value & (1 << bit):
                    data[byte_index] |= 1 << (7 - (bit_offset + (defn.bit_length - 1 - bit)) % 8)
                if (bit_offset + (defn.bit_length - bit)) % 8 == 0:
                    byte_index += 1