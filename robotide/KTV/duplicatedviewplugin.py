import wx

from robotide.pluginapi import Plugin, TreeAwarePluginMixin
from robotide.widgets import VerticalSizer

STYLE_STDERR = 2


class DuplicatedViewPlugin(Plugin, TreeAwarePluginMixin):
    title = 'Duplicated Actions'

    def __init__(self, application):
        Plugin.__init__(self, application)

    def _create_ui(self):
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.out = wx.Panel(panel)

        sizer.Add(self.out, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.notebook.add_tab(panel, self.title, allow_closing=False)

    def enable(self):
        self._create_ui()

    def disable(self):
        pass



