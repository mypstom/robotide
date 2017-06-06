import wx

import re
from extractinterface import ExtractInterface


class ExtractFrame(ExtractInterface):
    def __init__(self, impact_list):
        wx.Frame.__init__(self, parent=None, title='Extract User Keyword', size=(500, 400))
        self._rebuild_impact_list(impact_list)
        self.checkbox = None
        self.listbox = None
        self.user_keyword_name = None
        # self.args = None
        self.extract_controller = None
        self.steps = []
        self.args = []
        self.create_ui()

    def create_ui(self):
        panel = wx.Panel(self)
        name_panel = self.create_name_panel(panel)
        # arg_panel = self.create_arg_panel(panel)
        self.checkbox = wx.CheckBox(panel, label='Extract all')
        self.checkbox.SetValue(True)
        label = wx.StaticText(panel, label='TC/UK should be extract')
        label.SetForegroundColour((255, 0, 0))
        choices = [item[0] for item in self.impact_list]
        self.listbox = wx.ListBox(panel, size=(470, 200), choices=choices)
        self.listbox.SetSelection(choices.index(self.impact_list[0][0]))
        button_panel = self.create_button_panel(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(name_panel, 0, wx.ALL, 5)
        # sizer.Add(arg_panel, 0, wx.ALL, 5)
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

    """def create_arg_panel(self, parent):
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
        return panel"""

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
        # args = self.args.GetValue()
        args = ''

        self.get_extract_steps_and_args()
        temp = self.set_args_same_number()
        if temp != -1:
            print self.steps[temp] + ' have difference arg number!'
            return
        if self.checkbox.GetValue():
            module, lines = self.impact_list[0]
            controller = self.controller_dict[module]
            self.extract_controller = controller.extract_keyword(name, args, lines)
            for index in xrange(1, len(self.impact_list)):
                module, lines = self.impact_list[index]
                controller = self.controller_dict[module]
                controller._replace_steps_with_kw(name, lines)
            self.set_args()
        else:
            module, lines = self.impact_list[self.listbox.GetSelection()]
            controller = self.controller_dict[module]
            self.extract_controller = controller.extract_keyword(name, args, lines)
        self.Close()

    def set_args(self):
        new_args = []
        pattern = '\$\{[A-Za-z0-9]+\}'
        controllers_args = []
        for i in xrange(len(self.impact_list)):
            controllers_args.append([])
        for keyword_index in xrange(len(self.steps)):
            for arg_index in xrange(len(self.args[keyword_index][0])):
                args_set = set()
                for args in self.args[keyword_index]:
                    if args[arg_index] != '':
                        args_set.add(args[arg_index])
                if len(args_set) == 1:
                    if len(re.findall(pattern, list(args_set)[0])) == 0:
                        pass  # the arg is constant
                    else:
                        self.replace_step_args_with_new_args(keyword_index, arg_index, '${arg%d}' % (len(new_args)),
                                                             controllers_args)
                        new_args.append('${arg%d}' % (len(new_args)))
                else:
                    self.replace_step_args_with_new_args(keyword_index, arg_index, '${arg%d}' % (len(new_args)),
                                                         controllers_args)
                    new_args.append('${arg%d}' % (len(new_args)))
        while not self.merge_same_args(new_args, controllers_args):
            pass
        new_args = self.rename_new_args(new_args)
        self.set_extract_controller_args(new_args)
        self.set_controller_extract_step_args(controllers_args)

    def set_extract_controller_args(self, new_args):
        args = ' | '.join(new_args)
        self.extract_controller.arguments.set_value(args)

    def merge_same_args(self, new_args, controllers_args):
        arg_list = []
        for arg_index in xrange(len(new_args)):
            temp = []
            for controller in controllers_args:
                temp.append(controller[arg_index])
            if temp not in arg_list:
                arg_list.append(temp)
            else:
                index = arg_list.index(temp)
                self.merge_arg_in_extract_keyword(new_args[index], new_args[arg_index])
                self.rebuild_controllers_args(arg_index, controllers_args)
                del new_args[arg_index]
                return False
        return True

    def merge_arg_in_extract_keyword(self, arg, target_arg):
        for step in self.extract_controller.steps:
            for arg_index in xrange(len(step.args)):
                if step.args[arg_index] == target_arg:
                    step.args[arg_index] = arg

    def rename_new_args(self, new_args):
        arg_dict = {}
        count = 0
        for arg in new_args:
            arg_dict[arg] = '${arg%d}' % count
            count += 1
        for step in self.extract_controller.steps:
            for arg_index in xrange(len(step.args)):
                if step.args[arg_index] in arg_dict:
                    step.args[arg_index] = arg_dict[step.args[arg_index]]
        return [arg_dict[arg] for arg in new_args]

    def rebuild_controllers_args(self, index, controllers_args):
        for controllers_index in xrange(len(controllers_args)):
            del controllers_args[controllers_index][index]

    def set_controller_extract_step_args(self, controllers_args):
        for index in xrange(len(self.impact_list)):
            module = self.impact_list[index][0]
            controller = self.controller_dict[module]
            target = 0
            if '...' in module:
                target = int(module.split('...')[1])
            temp = 0
            for step in controller.steps:
                if step.keyword == self.extract_controller.name:
                    if temp == target:
                        for col in xrange(len(controllers_args[index])):
                            # if controllers_args[index][col] != '#default#':
                            step.change(col + 1, controllers_args[index][col])
                        break
                    temp += 1

    def check_args_only_have_variable(self, args, pattern):
        for arg in list(args):
            variables = re.findall(pattern, arg)
            if len(variables) == 0:
                return False
            for variable in variables:
                arg = arg.replace('${%s}' % variable, '')
            if arg != '':
                return False
        return True

    def replace_step_args_with_new_args(self, keyword_index, arg_index, arg_name, controllers_args):
        # set arg of controllers of use extract UK
        for index in xrange(len(self.args[keyword_index])):
            args = self.args[keyword_index][index]
            # if args[arg_index] != '#default#':
            # controllers_args[index].append(arg_name + '=' + args[arg_index])
            controllers_args[index].append(args[arg_index])
        # set extract UK new arg
        step = self.extract_controller.steps[keyword_index]
        step.args[arg_index] = arg_name

    def get_extract_steps_and_args(self):
        module, lines = self.impact_list[0][0], self.impact_list[0][1]
        controller = self.controller_dict[module]
        for index in xrange(lines[1] + 1):
            if index >= lines[0]:
                self.steps.append(controller.steps[index].keyword)
        for i in xrange(len(self.steps)):  # args = [keywords] , keyword = [controllers], controller = [args]
            self.args.append([])
        for module, lines in self.impact_list:
            controller = self.controller_dict[module]
            step_index = 0
            for index in xrange(lines[1] + 1):
                if index >= lines[0]:
                    step = controller.steps[index]
                    self.args[step_index].append(step.args)
                    step_index += 1

    def set_args_same_number(self):
        for keyword_index in xrange(len(self.steps)):
            args_len = []
            for controller_index in xrange(len(self.impact_list)):
                args_len.append(len(self.args[keyword_index][controller_index]))
            max_number = max(args_len)
            for index in xrange(len(args_len)):
                if args_len[index] < max_number:
                    # self.args[keyword_index][index].append('#default#')
                    return keyword_index
        return -1

    def cancel_click(self, event):
        self.Close()
