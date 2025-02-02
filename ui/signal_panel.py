import wx
import math
from simulator.signal import Signal
from simulator.database import J1939Database

class SignalPanel(wx.Panel):
    def __init__(self, parent, simulator, database):
        super().__init__(parent)
        self.simulator = simulator
        self.database = database  # Proper initialization
        self.controls_map = {}
        self._create_controls()
        
    def _create_controls(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        scrolled_panel = wx.ScrolledWindow(self)
        scrolled_panel.SetScrollRate(20, 20)
        
        grid = wx.FlexGridSizer(cols=2, vgap=10, hgap=15)
        
        # Create controls for UI-source signals
        for signal in self.simulator.signals:
            if signal.source != "ui":
                continue
                
            try:
                signal_def = self.database.get_signal_definition(
                    signal.pgn, 
                    signal.label
                )
                
                # Create UI elements
                label = wx.StaticText(scrolled_panel, 
                                    label=self._format_label(signal.label))
                ctrl = self._create_control_widget(scrolled_panel, signal_def, signal)
                
                grid.AddMany([(label, 0, wx.ALIGN_CENTER_VERTICAL),
                            (ctrl, 0, wx.EXPAND)])
                
                self.controls_map[signal.label] = ctrl
                
            except KeyError as e:
                wx.LogError(f"Signal definition not found: {e}")
                continue

        scrolled_panel.SetSizer(grid)
        main_sizer.Add(scrolled_panel, 1, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(main_sizer)
        scrolled_panel.Layout()

    def _format_label(self, signal_label: str) -> str:
        """Convert signal label to human-readable format"""
        return (signal_label.replace(".", " :: ")
                          .replace("_", " ")
                          .title()
                          .replace(" :: ", " - "))

    def _create_control_widget(self, parent, signal_def, signal):
        """Create appropriate control based on signal type"""
        # Calculate resolution-based control selection
        use_spinner = (
            signal_def.factor < 1.0 or 
            (signal_def.max_val - signal_def.min_val) > 100 or
            any(c in signal.label for c in ["temp", "press", "rate"])
        )
        
        if use_spinner:
            ctrl = wx.SpinCtrlDouble(parent, min=signal_def.min_val,
                                   max=signal_def.max_val, inc=signal_def.factor)
            ctrl.SetValue(signal.value)
            ctrl.SetDigits(self._calculate_decimal_places(signal_def))
            ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, 
                     lambda e: self._on_value_change(signal, e.GetValue()))
        else:
            ctrl = wx.Slider(parent, value=int(signal.value),
                           minValue=int(signal_def.min_val),
                           maxValue=int(signal_def.max_val),
                           style=wx.SL_HORIZONTAL|wx.SL_LABELS)
            ctrl.Bind(wx.EVT_SLIDER, 
                     lambda e: self._on_value_change(signal, e.GetInt()))
        
        ctrl.SetMinSize((300, -1))
        return ctrl

    def _calculate_decimal_places(self, signal_def):
        """Determine appropriate decimal places without numpy"""
        if signal_def.factor == 0:
            return 0
        magnitude = math.floor(math.log10(abs(signal_def.factor)))
        return max(0, -magnitude)

    def _on_value_change(self, signal, value):
        """Update simulator signal value"""
        signal.value = float(value)
        
    def update_control(self, signal):
        """Update UI control from simulator state"""
        if signal.label in self.controls_map:
            widget = self.controls_map[signal.label]
            current_value = signal.value
            
            if isinstance(widget, wx.SpinCtrlDouble):
                if widget.GetValue() != current_value:
                    widget.SetValue(current_value)
            elif isinstance(widget, wx.Slider):
                int_value = int(current_value)
                if widget.GetValue() != int_value:
                    widget.SetValue(int_value)