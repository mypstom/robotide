import wx


class ExtractInterface(wx.Frame):
    impact_list = []
    controller_dict = {}

    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='')

    def _rebuild_impact_list(self, impact_list):
        del self.impact_list[:]
        self.controller_dict.clear()
        for controller, durations in zip(impact_list.keys(), impact_list.values()):
            if len(durations) > 1:
                count = 0
                for duration in durations:
                    self.impact_list.append((controller.name + '...' + str(count), duration))
                    self.controller_dict[controller.name + '...' + str(count)] = controller
                    count += 1
            else:
                self.impact_list.append((controller.name, durations[0]))
                self.controller_dict[controller.name] = controller
        self.impact_list.sort(key=lambda v: v[1])
        self.impact_list.reverse()
