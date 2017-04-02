import wx


class ExtractFrame(wx.Frame):
    def __init__(self, controller, impact_list):
        wx.Frame.__init__(self, parent=None, title='Extract User Keyword', size=(500, 400))
        self.controller = controller
        self.impact_list = impact_list
        self.checkbox = None
        self.listbox = None
        self.user_keyword_name = None
        self.args = None
        self.create_ui()

    def create_ui(self):
        panel = wx.Panel(self)
        name_panel = self.create_name_panel(panel)
        arg_panel = self.create_arg_panel(panel)
        self.checkbox = wx.CheckBox(panel, label='Extract all')
        self.checkbox.SetValue(True)
        label = wx.StaticText(panel, label='TC/UK should be extract')
        label.SetForegroundColour((255, 0, 0))
        choices = [item.name for item in self.impact_list.keys()]
        self.listbox = wx.ListBox(panel, size=(470, 200), choices=choices)
        self.listbox.SetSelection(choices.index(self.controller.name))
        button_panel = self.create_button_panel(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(name_panel, 0, wx.ALL, 5)
        sizer.Add(arg_panel, 0, wx.ALL, 5)
        sizer.Add(self.checkbox, 0, wx.ALL, 5)
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.listbox, 1, wx.ALL, 5)
        sizer.Add(button_panel, 0, wx.ALL, 5)
        panel.SetSizerAndFit(sizer)

    def create_name_panel(self, parent):
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(panel, label='User keyword name :')
        self.user_keyword_name = wx.TextCtrl(panel, size=(340, -1))
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.user_keyword_name, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        return panel

    def create_arg_panel(self, parent):
        panel = wx.Panel(parent)
        up = wx.Panel(panel)
        down = wx.Panel(panel)
        up_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(up, label='Arguments :')
        self.args = wx.TextCtrl(up, size=(390, -1))
        up_sizer.Add(label, 0, wx.ALL, 5)
        up_sizer.Add(self.args, 0, wx.ALL, 5)
        up.SetSizer(up_sizer)
        hint_label = wx.StaticText(down, label='Example : ${arg1} | ${arg2} ....etc.')
        font = wx.Font(10, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        hint_label.SetFont(font)
        down_sizer = wx.BoxSizer(wx.HORIZONTAL)
        down_sizer.Add(hint_label, 1, wx.EXPAND)
        down.SetSizer(down_sizer)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(up, 0, wx.EXPAND)
        sizer.Add(down, 0, wx.EXPAND)
        panel.SetSizer(sizer)
        return panel

    def create_button_panel(self, parent):
        panel = wx.Panel(parent)
        panel.SetSize((500, -1))
        ok_button = wx.Button(panel, label='OK')
        cancel_button = wx.Button(panel, label='Cancel')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Panel(panel), 1, wx.ALL, 5)
        sizer.Add(ok_button, 1, wx.ALL, 5)
        sizer.Add(wx.Panel(panel), 1, wx.ALL, 5)
        sizer.Add(cancel_button, 1, wx.ALL, 5)
        sizer.Add(wx.Panel(panel), 1, wx.ALL, 5)
        panel.SetSizer(sizer)
        ok_button.Bind(wx.EVT_BUTTON, self.ok_click)
        cancel_button.Bind(wx.EVT_BUTTON, self.cancel_click)
        return panel

    def ok_click(self, event):
        name = self.user_keyword_name.GetValue()
        args = self.args.GetValue()
        if self.checkbox.GetValue():
            controller, lines = self.impact_list.items()[0]
            controller.extract_keyword(name, args, lines)
            for index in xrange(1, len(self.impact_list)):
                controller, lines = self.impact_list.items()[index]
                controller._replace_steps_with_kw(name, lines)
        else:
            controller, lines = self.impact_list.items()[self.listbox.GetSelection()]
            controller.extract_keyword(name, args, lines)
        self.Close()

    def cancel_click(self, event):
        self.Close()
