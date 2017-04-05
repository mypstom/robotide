import wx


class ExtractListView(wx.Frame):
    def __init__(self, impact_list):
        wx.Frame.__init__(self, parent=None, title='Extract Detail', size=(550, 400))
        self.impact_list = impact_list
        self.listbox = None
        self.list_ctrl = None
        self.create_ui()

    def create_ui(self):
        panel = wx.Panel(self)
        left = wx.Panel(panel)
        right = wx.Panel(panel)
        choices = [item.name for item in self.impact_list.keys()]
        self.listbox = wx.ListBox(left, size=(100, 300), choices=choices)
        self.listbox.Bind(wx.EVT_LISTBOX, self.list_box_selection_changed)
        left_label = wx.StaticText(left, label='TC/UK')
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(left_label, 0, wx.ALL, 5)
        left_sizer.Add(self.listbox, 0, wx.ALL, 5)
        left.SetSizer(left_sizer)
        right_label = wx.StaticText(right, label='Extract lines detail')
        self.list_ctrl = wx.ListCtrl(right, size=(400, 300), style=wx.LC_REPORT)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(right_label, 0, wx.ALL, 5)
        right_sizer.Add(self.list_ctrl, 0, wx.ALL, 5)
        right.SetSizer(right_sizer)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left, 0, wx.ALL, 5)
        sizer.Add(right, 0, wx.ALL, 5)
        panel.SetSizer(sizer)

    def list_box_selection_changed(self, event):
        self.list_ctrl.ClearAll()
        controller, duration = self.impact_list.items()[self.listbox.GetSelection()]
        lines, max_col = self.get_extract_lines(controller, duration[0] - 1,
                                                duration[1] - 1)  # because duration is start at 1 not 0
        self.list_ctrl.InsertColumn(0, 'Keyword')
        for index in xrange(1, max_col):
            self.list_ctrl.InsertColumn(index, 'arg%d' % index)
        for line in lines:
            self.list_ctrl.Append(line)
        for index in xrange(max_col):
            self.list_ctrl.SetColumnWidth(index, wx.LIST_AUTOSIZE)

    def get_extract_lines(self, controller, start, end):
        lines = []
        max_col = 0
        for index in xrange(end + 1):
            if index >= start:
                temp = []
                step = controller.steps[index]
                temp.append(step.keyword)
                temp.extend(step.args)
                lines.append(temp)
                max_col = max(max_col, len(temp))
        return lines, max_col
