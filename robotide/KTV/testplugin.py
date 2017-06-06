import wx

from robotide.pluginapi import Plugin, TreeAwarePluginMixin


class TestPlugin(Plugin, TreeAwarePluginMixin):
    title = 'Test'

    def __init__(self, application):
        Plugin.__init__(self, application)

    def _create_ui(self):
        panel = wx.Panel(self.notebook)
        self.notebook.add_tab(panel, self.title, allow_closing=False)

    def enable(self):
        self._create_ui()
        pass

    def disable(self):
        pass
