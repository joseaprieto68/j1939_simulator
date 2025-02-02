import json
from dataclasses import dataclass

@dataclass
class SignalDefinition:
    start_bit: int
    bit_length: int
    is_little_endian: bool
    factor: float
    offset: float
    min: float
    max: float

class J1939Database:
    def __init__(self, database_path: str):
        self.signals = self._load_database(database_path)
    
    def _load_database(self, path: str) -> dict:
        """Returns {pgn: {signal_label: SignalDefinition}}"""
        with open(path) as f:
            data = json.load(f)
        
        return {
            pgn_def["pgn"]: {
                sig["label"]: SignalDefinition(
                    start_bit=sig["startBit"],
                    bit_length=sig["bitLength"],
                    is_little_endian=self._is_little_endian(sig),
                    factor=sig["factor"],
                    offset=sig["offset"],
                    min=sig["min"],
                    max=sig["max"]
                )
                for sig in pgn_def["signals"]
            }
            for pgn_def in data["pgns"]
        }

    def _is_little_endian(self, signal: dict) -> bool:
        """Determine endianness based on signal properties"""
        # Implement based on your specific protocol rules
        return True  # Default to little-endian