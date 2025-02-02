from dataclasses import dataclass
from config.pgn_definitions import PGN_CONFIG

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
        self.get_active_signals = self.get_active_signals
    
    def _load_from_config(self):
        """Load and initialize signals from PGN configuration"""
        signals = []
        
        for pgn in PGN_CONFIG:
            for signal_def in PGN_CONFIG[pgn]:
                # Create signal with initial value based on source type
                initial_value = 1.0 if signal_def["source"] == "fixed" else 0.0
                
                signals.append(
                    Signal(
                        pgn=pgn,
                        label=signal_def["label"],
                        source=signal_def["source"],
                        value=initial_value
                    )
                )
        
        return signals

    def get_active_signals(self, pgn: int) -> dict:
        """Get enabled signals for a specific PGN"""
        return {
            signal.label: signal.value
            for signal in self.signals
            if signal.pgn == pgn and signal.source != "fixed"
        }