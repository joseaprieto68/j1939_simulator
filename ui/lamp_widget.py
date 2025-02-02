import wx
import wx.lib.newevent as ne
from enum import Enum
from pathlib import Path

# Custom events
LampUpdateEvent, EVT_LAMP_UPDATE = ne.NewCommandEvent()

class LampState(Enum):
    OFF = 0
    STEADY = 1
    SLOW_FLASH = 2
    FAST_FLASH = 3

class LampWidget(wx.Panel):
    def __init__(self, parent, lamp_type: str):
        super().__init__(parent)
        self.lamp_type = lamp_type  # 'PL', 'AWL', 'RSL', 'MIL'
        self.current_state = LampState.OFF
        self.timer = wx.Timer(self)
        self.flashing = False
        
        # Load lamp images
        self._load_images()
        self._setup_ui()
        self._bind_events()

    def _load_images(self):
        """Load PNG images from resources folder"""
        base_path = Path(__file__).parent.parent / "resources"
        try:
            self.off_bmp = wx.Bitmap(str(base_path / "lamp_off.png"), wx.BITMAP_TYPE_PNG)
            self.on_bmp = wx.Bitmap(str(base_path / f"lamp_{self.lamp_type.lower()}.png"), wx.BITMAP_TYPE_PNG)
        except:
            self.off_bmp = wx.Bitmap(32, 32)  # Fallback
            self.on_bmp = wx.Bitmap(32, 32)
            self.on_bmp.SetBackgroundColour(wx.RED if "RED" in self.lamp_type else wx.YELLOW)

    def _setup_ui(self):
        """Initialize visual components"""
        self.SetBackgroundColour(wx.WHITE)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.bitmap = wx.StaticBitmap(self, bitmap=self.off_bmp)
        self.sizer.Add(self.bitmap, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.SetSizer(self.sizer)

    def _bind_events(self):
        """Event binding"""
        self.Bind(wx.EVT_TIMER, self._on_timer, self.timer)
        self.Bind(EVT_LAMP_UPDATE, self._on_update_state)

    def _on_timer(self, event):
        """Handle flashing animation"""
        if self.bitmap.GetBitmap().IsSameAs(self.on_bmp):
            self.bitmap.SetBitmap(self.off_bmp)
        else:
            self.bitmap.SetBitmap(self.on_bmp)
        self.Refresh()

    def _on_update_state(self, event):
        """Handle state update from main application"""
        state = LampState(event.GetInt())
        self.update_state(state)

    def update_state(self, state: LampState):
        """Update lamp state programmatically"""
        self.current_state = state
        
        # Stop any existing timer
        if self.timer.IsRunning():
            self.timer.Stop()

        # Handle new state
        if state == LampState.OFF:
            self.bitmap.SetBitmap(self.off_bmp)
        elif state == LampState.STEADY:
            self.bitmap.SetBitmap(self.on_bmp)
        else:  # Flashing states
            interval = 1000 if state == LampState.SLOW_FLASH else 500  # ms
            self.timer.Start(interval)
        
        self.Refresh()

    def GetState(self) -> LampState:
        """Return current lamp state"""
        return self.current_state

# Example usage
if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    
    panel = wx.Panel(frame)
    sizer = wx.GridSizer(rows=2, cols=2, gap=(10, 10))
    
    for lamp in ["PL", "AWL", "RSL", "MIL"]:
        widget = LampWidget(panel, lamp)
        widget.update_state(LampState.FAST_FLASH)
        sizer.Add(widget, 0, wx.ALIGN_CENTER)
    
    panel.SetSizer(sizer)
    frame.Show()
    app.MainLoop()