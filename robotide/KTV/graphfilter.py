import wx

from robotide.pluginapi import Plugin, TreeAwarePluginMixin
from robotide.publish import GenerateSpecificGraph


class GraphFilter(Plugin, TreeAwarePluginMixin):
    title = 'Graph Filter'

    def __init__(self, application):
        Plugin.__init__(self, application)

    def _create_ui(self):
        panel = wx.Panel(self.notebook)
        button = wx.Button(panel, label='Generate')
        button.Bind(wx.EVT_BUTTON, self.generate_button_click)
        self.notebook.add_tab(panel, self.title, allow_closing=False)

    def generate_button_click(self, event):
        data = ['ClickSuggestWordAtCell', 'DoubleClickSuggestListItem', 'AssertSuggestListItem',
                'SaveFileByNameDirectly', 'myKeyword1']
        GenerateSpecificGraph(node_list=data).publish()

    def enable(self):
        self._create_ui()

    def disable(self):
        pass
