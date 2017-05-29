import wx
from robotide.publish import SettingDuplicatedDetectionThreshold


class ConfigSetting(wx.Frame):
    threshold = None

    def __init__(self, threshold):
        wx.Frame.__init__(self, parent=None, title='Config Setting', size=(350, 120))
        self.threshold = threshold
        self.spinctrl = None
        self.create_ui()

    def create_ui(self):
        panel = wx.Panel(self)
        up = wx.Panel(panel)
        down = wx.Panel(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(up, label='duplicated detection threshold : ')
        self.spinctrl = wx.SpinCtrl(up)
        self.spinctrl.SetRange(2, 100)
        self.spinctrl.SetValue(self.threshold)
        button = wx.Button(down, label='OK')
        up_sizer = wx.BoxSizer(wx.HORIZONTAL)
        up_sizer.Add(label, 0, wx.ALL, 5)
        up_sizer.Add(self.spinctrl, 0, wx.ALL, 5)
        up.SetSizer(up_sizer)
        down_sizer = wx.BoxSizer(wx.HORIZONTAL)
        down_sizer.Add(wx.Panel(down), 1, wx.ALL, 5)
        down_sizer.Add(button, 1, wx.ALL, 5)
        down_sizer.Add(wx.Panel(down), 1, wx.ALL, 5)
        down.SetSizer(down_sizer)
        sizer.Add(up, 1, wx.ALL, 5)
        sizer.Add(down, 1, wx.ALL, 5)
        panel.SetSizer(sizer)
        button.Bind(wx.EVT_BUTTON, self.ok_button_click)

    def ok_button_click(self, event):
        SettingDuplicatedDetectionThreshold(threshold=self.spinctrl.GetValue()).publish()
        self.Close()
