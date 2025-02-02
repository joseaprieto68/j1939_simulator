# Diagnostic Trouble Code configurations
DTC_EVENTS = [
    {
        "name": "Low Fuel Level Shutdown",
        "spn": 96,
        "fmi": 1,
        "lamps": {"PL": "OFF", "AWL": "OFF", "RSL": "ON-STEADY", "MIL": "OFF"}
    },
    # Add more DTC events here
]
