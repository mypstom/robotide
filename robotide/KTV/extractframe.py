import wx


class ExtractFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='Extract User Keyword', size=(500, 400))
        panel = wx.Panel(self)
        name_panel = self.create_name_panel(panel)
        arg_panel = self.create_arg_panel(panel)
        self.text_ctrl = wx.stc.StyledTextCtrl(panel, size=(470, -1))
        button_panel = self.create_button_panel(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(name_panel, 0, wx.ALL, 5)
        sizer.Add(arg_panel, 0, wx.ALL, 5)
        sizer.Add(self.text_ctrl, 1, wx.ALL, 5)
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
        label = wx.StaticText(up, label='Arg :')
        self.args = wx.TextCtrl(up, size=(430, -1))
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

    def set_text(self, text):
        print text
        self.text_ctrl.SetText(text)

    def ok_click(self, event):
        print self.user_keyword_name.GetValue()
        print self.args.GetValue()
        print self.text_ctrl.GetText()
        self.Close()

    def cancel_click(self, event):
        print self.text_ctrl.GetText()
        self.Close()
