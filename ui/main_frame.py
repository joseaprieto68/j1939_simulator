import wx
from ui.signal_panel import SignalPanel
from ui.lamp_widget import LampWidget

class MainFrame(wx.Frame):
    def __init__(self, parent, simulator, dtc_handler):
        super().__init__(parent, title="J1939 Simulator")
        self.simulator = simulator
        self.dtc_handler = dtc_handler
        
        self._create_ui()
        self.Layout()
        self.Centre()
        
    def _create_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Connection status
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusText("PCAN-USB: Connected", 0)
        self.status_bar.SetStatusText("SA: 0x80", 1)
        
        # Main content
        splitter = wx.SplitterWindow(panel)
        
        # Signal controls
        self.signal_panel = SignalPanel(splitter, self.simulator)
        
        # DTC controls
        dtc_panel = wx.Panel(splitter)
        self._create_dtc_controls(dtc_panel)
        
        splitter.SplitVertically(self.signal_panel, dtc_panel, sashPosition=400)
        main_sizer.Add(splitter, 1, wx.EXPAND)
        panel.SetSizer(main_sizer)
        
    def _create_dtc_controls(self, parent):
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Lamp status
        lamp_box = wx.StaticBox(parent, label="Diagnostic Lamps")
        lamp_sizer = wx.GridSizer(rows=2, cols=2, gap=(10, 10))
        self.lamps = {
            "RSL": LampWidget(lamp_box, "RSL"),
            "AWL": LampWidget(lamp_box, "AWL"),
            "PL": LampWidget(lamp_box, "PL"),
            "MIL": LampWidget(lamp_box, "MIL")
        }
        for lamp in self.lamps.values():
            lamp_sizer.Add(lamp, 0, wx.ALIGN_CENTER)
        lamp_box.SetSizer(lamp_sizer)
        
        # DTC event buttons
        dtc_box = wx.StaticBox(parent, label="DTC Events")
        dtc_sizer = wx.FlexGridSizer(cols=2, vgap=5, hgap=10)
        self.dtc_buttons = {}
        for event in self.dtc_handler.events:
            btn = wx.ToggleButton(dtc_box, label=event["name"])
            btn.Bind(wx.EVT_TOGGLEBUTTON, 
                    lambda e, evt=event: self._on_dtc_toggle(e, evt))
            dtc_sizer.Add(btn, 0, wx.EXPAND)
        dtc_box.SetSizer(dtc_sizer)
        
        sizer.Add(lamp_box, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(dtc_box, 1, wx.EXPAND|wx.ALL, 5)
        parent.SetSizer(sizer)
        
    def _on_dtc_toggle(self, event, dtc_event):
        self.dtc_handler.update_dtc_state(
            dtc_event["name"], 
            event.GetEventObject().GetValue()
        )
        
    def update_lamps(self, states):
        for lamp_type, state in states.items():
            self.lamps[lamp_type].update_state(state)