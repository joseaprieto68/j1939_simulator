from config.dtc_definitions import DTC_EVENTS

class DTCHandler:
    def __init__(self):
        self.events = DTC_EVENTS
        self.active_dtcs = []
        self.occurrence_counters = {e["name"]: 0 for e in DTC_EVENTS}
    
    def update_dtc_state(self, event_name: str, active: bool):
        if active:
            self.occurrence_counters[event_name] += 1
            if not any(d["name"] == event_name for d in self.active_dtcs):
                self.active_dtcs.append({
                    "name": event_name,
                    "count": self.occurrence_counters[event_name]
                })
        else:
            self.active_dtcs = [d for d in self.active_dtcs if d["name"] != event_name]
    
    def get_dm1_data(self):
        # Implementation using DTC_EVENTS and active_dtcs
        # Returns (lamp_states, dtc_list)
        pass