from dataclasses import dataclass

@dataclass
class Signal:
    pgn: int
    label: str
    value: float
    source: str

class Simulator:
    def __init__(self, database):
        self.database = database
        self.signals = self._load_from_config()
    
    def _load_from_config(self):
        # Loads signals from PGN_definitions.py
        return []