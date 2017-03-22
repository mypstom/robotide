# -*- coding: utf-8 -*-　

import math
import os
import itertools


class DynamicAnalyzer:
    TS_list = list()
    TC_list = list()
    UK_list = list()
    LK_list = list()
    C_set = set()
    node_level = dict()  # key : node, value : level
    nodes = set()
    edges = dict()  # key : (node1, node2), value : weighted number
    nodesWithType = dict()  # key : node, value : type
    serial_number = dict()

    def __init__(self):
        self.serial_number_flag = True  # 使node顯示名稱變成流水號
        self.action_count = 0

    def get_change_impact_dict(self, change_list):
        change_impact_dict = dict()
        limit_level = 1
        while True:
            change_impact = self.set_change_impact_node(dict(self.edges), change_list, 0, 0, limit_level)
            if limit_level - 1 in change_impact_dict.keys():
                if change_impact_dict[limit_level - 1] == change_impact:
                    break
            if limit_level not in change_impact_dict.keys():
                change_impact_dict[limit_level] = 0
            change_impact_dict[limit_level] += change_impact
            limit_level += 1
        for key in change_impact_dict.keys():  # remove LK~C response relation
            if key == 1:
                continue
            change_impact_dict[key] -= change_impact_dict[1]
        return change_impact_dict

    def set_change_impact_node(self, edges, change_list, change_impact, level, limit_level):
        if level >= limit_level:
            return change_impact
        for change in change_list:
            new_change_list = list()
            if self.nodesWithType[change] == 'TestSuite':
                continue
            else:
                index = 0
                while index < len(edges.keys()):
                    edge = edges.keys()[index]
                    if edge[1] == change:
                        if edge[0] not in change_list:
                            new_change_list.append(edge[0])
                        change_impact += edges[edge]
                        edges.pop(edge, None)
                        index -= 1
                    index += 1

            if len(new_change_list) > 0:
                change_impact = self.set_change_impact_node(edges, new_change_list, change_impact, level + 1,
                                                            limit_level)
        return change_impact

    def read_excluded_library_keyword_file(self):
        excluded_node_not_show = set()
        excluded_node_show = set()
        with open('ExcludedLibraryKeyword.txt', 'r+') as f:
            for line in f:
                if '#' in line:
                    line = line[:line.index('#')]
                if line != '\n':
                    if ', ShowNode=' in line:
                        line = line[:line.index(', ShowNode=')]
                        excluded_node_show.add(line.strip('\n').strip())
                    elif ',' in line:
                        raise Exception('ExcludedLibraryKeyword.txt format error!')
                    else:
                        excluded_node_not_show.add(line.strip('\n').strip())
        return excluded_node_show, excluded_node_not_show

    def generate_full_graph(self):
        level_node = self.tree_layout(self.edges, self.node_level)
        node_list = []
        for value in level_node.values():
            node_list.extend(value)
        return node_list, self.edges, self.nodesWithType

    def generate_specific_graph(self, node_list):
        # print 'generate_specific_graph'
        specific_nodes, specific_edges = self.specific_tree_data(node_list)
        # print 'specific_tree_data finish'
        specific_node_level = self.build_specific_node_level(specific_nodes)
        # print specific_node_level
        # print 'build_specific_node_level finish'
        self.add_fake_top_node(specific_nodes, specific_edges, specific_node_level)
        # print specific_node_level
        # print 'add_fake_top_node finish'
        level_node = self.tree_layout(specific_edges, specific_node_level)
        print level_node
        print 'tree_layout finish'
        level_node = self.remove_fake_top_node(specific_nodes, specific_edges, specific_node_level, level_node)
        node_list = []
        for value in level_node.values():
            node_list.extend(value)
        return node_list, specific_edges, self.nodesWithType

    def add_fake_top_node(self, nodes, edges, node_level):
        fake_node = 'Fake_node'
        nodes.add(fake_node)
        temp = set()
        for node in nodes:
            has_parent = False
            for edge in edges:
                if edge[1] == node:
                    has_parent = True
                    break
            if not has_parent:
                temp.add(node)
        for node in temp:
            edges[(fake_node, node)] = 1
        for node in node_level:
            node_level[node] += 1
        node_level[fake_node] = 0

    def remove_fake_top_node(self, nodes, edges, node_level, level_node):
        fake_node = 'Fake_node'
        new_level_node = dict()
        for level in level_node:
            new_level_node[level - 1] = level_node[level][:]
        del new_level_node[-1]
        for node in node_level:
            node_level[node] -= 1
        del node_level[fake_node]
        temp = []
        for edge in edges:
            if edge[0] == fake_node:
                temp.append(edge)
        for edge in temp:
            del edges[edge]
        nodes.remove(fake_node)
        return new_level_node

    def specific_tree_data(self, node_list):
        if self.serial_number_flag:
            node_list = [self.serial_number[node] for node in node_list]
        specific_edges = dict()
        for edge in self.edges.keys():
            if edge[0] in node_list or edge[1] in node_list:
                specific_edges[edge] = self.edges[edge]
        specific_nodes = set(node_list)
        for edge in specific_edges:
            if edge[0] not in specific_nodes:
                specific_nodes.add(edge[0])
            if edge[1] not in specific_nodes:
                specific_nodes.add(edge[1])
        return specific_nodes, specific_edges

    def find_node_level_range(self, node_set):
        temp = set()
        for node in node_set:
            temp.add(self.node_level[node])
        return list(temp)[0], list(temp)[len(temp) - 1]

    def build_specific_node_level(self, node_set):
        start_level, end_level = self.find_node_level_range(node_set)
        new_level = 0
        new_node_level = dict()
        for level in xrange(start_level, end_level + 1):
            for node in node_set:
                if self.node_level[node] == level:
                    new_node_level[node] = new_level
            new_level += 1
        return new_node_level

    def build_model(self, filepath):
        excluded_node_show, excluded_node_not_show = self.read_excluded_library_keyword_file()
        source = os.path.abspath(filepath)

        with open(source + '\Excute.txt', 'r+') as f:
            for line in f:
                if line != '\n':
                    data_list = line.split('\t')
                    if data_list[0].split('=')[1].strip('\n') in excluded_node_not_show:
                        continue
                    if data_list[0].split('=')[0] == 'TS':
                        self.TS_list.append(data_list[0].split('=')[1].strip('\n'))
                    elif data_list[0].split('=')[0] == 'TC':  # TC_list = [parent , TC_name]
                        self.TC_list.append(
                            [data_list[1].split('=')[1].strip('\n'), data_list[0].split('=')[1].strip('\n')])
                    else:
                        args = ''
                        if len(data_list[1].split('=')) > 2:  # if arg has '=', append all arg
                            for index in range(1, len(data_list[1].split('='))):
                                args += data_list[1].split('=')[index]
                                args += '='
                            args = args[1:len(args) - 2]  # remove '[' and ']'
                        else:
                            args = data_list[1].split('=')[1].strip('\n')
                            args = args[1:len(args) - 1]  # remove '[' and ']'
                        if data_list[0].split('=')[0] == 'UK':  # UK_list = [parent , UK_name, args]
                            self.UK_list.append(
                                [data_list[2].split('=')[1].strip('\n'), data_list[0].split('=')[1].strip('\n'), args])
                        elif data_list[0].split('=')[0] == 'LK':  # LK_list = [parent , LK_name, args]
                            self.LK_list.append(
                                [data_list[2].split('=')[1].strip('\n'), data_list[0].split('=')[1].strip('\n'),
                                 args])
                            if len(args) > 0 and data_list[0].split('=')[1].strip('\n') not in excluded_node_show:
                                self.C_set.add(args.split(',')[0])

        print 'EVENT : %r' % len(self.LK_list)
        self.action_count = len(self.LK_list)

        if self.serial_number_flag:
            for index in range(len(self.TS_list)):
                self.serial_number[self.TS_list[index]] = 'S' + '{:02d}'.format(index)
                self.TS_list[index] = self.serial_number[self.TS_list[index]]
            for index in range(len(self.TC_list)):
                self.serial_number[self.TC_list[index][1]] = 'T' + '{:02d}'.format(index)
                if self.TC_list[index][0] in self.serial_number:
                    self.TC_list[index][0] = self.serial_number[self.TC_list[index][0]]
                    self.TC_list[index][1] = self.serial_number[self.TC_list[index][1]]
            count = 0
            for index in range(len(self.UK_list)):
                if self.UK_list[index][1] not in self.serial_number:
                    self.serial_number[self.UK_list[index][1]] = 'U' + '{:02d}'.format(count)
                    count += 1
                self.UK_list[index][1] = self.serial_number[self.UK_list[index][1]]
            for index in range(len(self.UK_list)):
                if self.UK_list[index][0] in self.serial_number:
                    self.UK_list[index][0] = self.serial_number[self.UK_list[index][0]]
            C_list = list(self.C_set)
            for index in xrange(len(C_list)):
                self.serial_number[C_list[index]] = 'C' + '{:03d}'.format(index)
                C_list[index] = self.serial_number[C_list[index]]
            self.C_set = set(C_list)
            count = 0
            for index in range(len(self.LK_list)):
                if self.LK_list[index][1] not in self.serial_number:
                    self.serial_number[self.LK_list[index][1]] = 'L' + '{:02d}'.format(count)
                    count += 1
                if self.LK_list[index][0] in self.serial_number:
                    self.LK_list[index][0] = self.serial_number[self.LK_list[index][0]]
                args = self.LK_list[index][2].split(',')
                for arg in args:
                    if arg in self.serial_number:
                        self.LK_list[index][2] = self.LK_list[index][2].replace(arg, self.serial_number[arg])
                self.LK_list[index][1] = self.serial_number[self.LK_list[index][1]]

        # print serial_number

        for TS in self.TS_list:
            self.nodes.add(TS)
            self.nodesWithType[TS] = 'TestSuite'
        for TC in self.TC_list:
            self.nodes.add(TC[1])
            self.nodesWithType[TC[1]] = 'TestCase'
        for LK in self.UK_list:
            self.nodes.add(LK[1])
            self.nodesWithType[LK[1]] = 'Userkeyword'
        for LK in self.LK_list:
            self.nodes.add(LK[1])
            self.nodesWithType[LK[1]] = 'Librarykeyword'
        for C in self.C_set:
            self.nodes.add(C)
            self.nodesWithType[C] = 'Component'

        TS_set = set(self.TS_list)
        print 'TS:%r' % len(TS_set)
        TC_set = set()
        for item in self.TC_list:
            TC_set.add(item[1])
        print 'TC:%r' % len(TC_set)
        UK_set = set()
        for item in self.UK_list:
            UK_set.add(item[1])
        print 'UK:%r' % len(UK_set)
        LK_set = set()
        for item in self.LK_list:
            LK_set.add(item[1])
        print 'LK:%r' % len(LK_set)
        print 'C:%r' % len(self.C_set)

        for TS in self.TS_list:
            self.set_level(TS, 0)
        # print node_level
        self.build_edges()
        # print 'weighted coupling = %r\n--------------------' % self.get_weighted(None, None, edges)
        self.remove_redundant_edges()
        # print 'temp = %r' % self.get_weighted('NewCrosswordByValidGridSize', 'SelectCrosswordSageWindow', edges)
        # print edges
        print 'edges number : %d' % len(self.edges)
        print 'nodes number : %d' % len(self.node_level.keys())

        """change_list = list()
        change_list.append('btnSuggestWords')
        # change_list.append('btnFind')
        # change_list.append('btnAddWord')
        # change_list.append('File|New Crossword')
        change_impact_dict = self.get_change_impact_dict(nodes, edges, nodesWithType, change_list)
        #nodesWithType['btnSuggestWords'] = 'Changed'
        print change_impact_dict
        change_impact_dict = self.get_change_impact_by_formula(edges, change_list)
        print change_impact_dict"""
        """change_impact_dict = self.get_change_impact_dict(nodes, edges, nodesWithType, ['File|New Crossword'])
        #nodesWithType['File|New Crossword'] = 'Changed'
        print change_impact_dict
        change_impact_dict = self.get_change_impact_by_formula(edges, ['File|New Crossword'])
        print change_impact_dict"""

    def set_level(self, current, current_level):
        node_type = self.nodesWithType[current]
        if current not in self.node_level.keys():
            self.node_level[current] = current_level
        else:
            self.node_level[current] = max(self.node_level[current], current_level)
        child_node_set = set()
        if node_type == 'TestSuite':
            for TC in self.TC_list:
                if TC[0] == current:
                    child_node_set.add(TC[1])
        elif node_type == 'TestCase' or node_type == 'Userkeyword':
            index = 0
            while index < len(self.UK_list):
                UK = self.UK_list[index]
                if UK[0] == current:
                    if UK[1] not in child_node_set:
                        child_node_set.add(UK[1])
                index += 1
            index = 0
            while index < len(self.LK_list):
                LK = self.LK_list[index]
                if LK[0] == current:
                    if LK[1] not in child_node_set:
                        child_node_set.add(LK[1])
                index += 1
        elif node_type == 'Librarykeyword':
            for LK in self.LK_list:
                if LK[1] == current:
                    for C in self.C_set:
                        if LK[2].split(',')[0] == C:
                            child_node_set.add(C)

        for node in child_node_set:
            self.set_level(node, current_level + 1)

    def build_edges(self):
        current_level_list = list()
        current_level = 0

        for LK in self.LK_list:
            for C in self.C_set:
                if LK[2].split(',')[0] == C and (LK[1], C) not in self.edges.keys():
                    self.edges[(LK[1], C)] = 1
                    break

        for key in self.node_level.keys():
            if self.node_level[key] == current_level:
                current_level_list.append(key)
        while len(current_level_list) > 0:
            for current in current_level_list:
                # print current
                node_type = self.nodesWithType[current]
                if node_type == 'TestSuite':
                    for TC in self.TC_list:
                        if TC[0] == current:
                            self.edges[(current, TC[1])] = 1
                elif node_type == 'TestCase' or node_type == 'Userkeyword':
                    index = 0
                    child_node_set = set()
                    while index < len(self.UK_list):
                        UK = self.UK_list[index]
                        if UK[0] == current:
                            if (current, UK[1]) not in self.edges.keys():
                                self.edges[(current, UK[1])] = 1
                            else:
                                self.edges[(current, UK[1])] += 1
                            if UK[1] not in child_node_set:
                                child_node_set.add(UK[1])
                            else:
                                del self.UK_list[index]
                                index -= 1
                        index += 1
                    index = 0
                    child_node_set.clear()
                    while index < len(self.LK_list):
                        LK = self.LK_list[index]
                        if LK[0] == current:
                            if (current, LK[1]) not in self.edges.keys():
                                self.edges[(current, LK[1])] = 1
                            else:
                                self.edges[(current, LK[1])] += 1
                            if LK[1] not in child_node_set:
                                child_node_set.add(LK[1])
                            else:
                                del self.LK_list[index]
                                index -= 1
                        index += 1
            current_level += 1
            del current_level_list[:]
            for key in self.node_level.keys():
                if self.node_level[key] == current_level:
                    current_level_list.append(key)

    def remove_redundant_edges(self):
        change_list = list()
        max_level = 0
        for level in self.node_level.values():
            max_level = max(max_level, level)
        for level in range(max_level, 1, -1):
            del change_list[:]
            for key in self.node_level.keys():
                if self.node_level[key] == level:
                    change_list.append(key)
            for change in change_list:
                parent_list = list()
                if self.nodesWithType[change] == 'Librarykeyword':
                    for LK in self.LK_list:
                        if LK[1] == change:
                            parent_list.append(LK[0])
                elif self.nodesWithType[change] == 'Userkeyword':
                    for UK in self.UK_list:
                        if UK[1] == change:
                            parent_list.append(UK[0])
                else:
                    continue
                for parent in parent_list:
                    scale = self.get_weighted(None, parent, self.edges)
                    if scale == 1:
                        continue
                    weight = self.get_weighted(parent, change, self.edges)
                    self.edges[(parent, change)] = weight / scale

    def get_weighted(self, node1, node2, edges):
        count = 0
        for edge in edges.keys():
            if node1 is None and node2 is None:
                count += edges[edge]
            elif node1 is None:
                if edge[1] == node2:
                    count += edges[edge]
            else:
                if edge[0] == node1 and edge[1] == node2:
                    count += edges[edge]
        return count

    def calculate_coupling(self, nodes, edges):
        # unweighted_coupling = float(len(edges.keys())) / (len(nodes_set) * (len(nodes_set) - 1))
        unweighted_coupling = float(len(edges.keys())) / (len(nodes) * (len(nodes) - 1))
        print 'unweighted coupling = %r' % unweighted_coupling
        # weighted_coupling = float(self.get_weighted(None, None, edges)) / self.action_count
        weighted_coupling = self.get_weighted(None, None, edges)
        print 'weighted coupling = %r' % weighted_coupling
        return weighted_coupling, unweighted_coupling

    def get_change_impact_by_formula(self, change_list, edges):
        change_impact_dict = dict()
        edges_set = set()
        limit_level = 1
        while True:
            edges_set = self.calculate_change_impact_by_formula(edges_set, change_list, change_impact_dict,
                                                                limit_level, edges)
            if limit_level - 1 in change_impact_dict.keys():
                if change_impact_dict[limit_level] == change_impact_dict[limit_level - 1]:
                    break
            limit_level += 1
        change_impact_dict.pop(limit_level)
        for key in change_impact_dict.keys():  # remove LK~C response relation
            if key == 1:
                continue
            change_impact_dict[key] -= change_impact_dict[1]
        return change_impact_dict

    def calculate_change_impact_by_formula(self, edges_set, change_list, change_impact_dict, level, edges):
        for change in change_list:
            temp_set = self.get_edges(change, edges)
            edges_set = edges_set.union(temp_set)
        weight = 0
        del change_list[:]
        for edge in edges_set:
            change_list.append(edge[0])
            weight += edges[(edge[0], edge[1])]
        change_impact_dict[level] = weight
        return edges_set

    def get_edges(self, node, edges):
        result = set()
        for edge in edges.keys():
            if edge[1] == node:
                result.add(edge)
        return result

    def build_node_parent_dict(self, edges, node_level, max_level):
        node_parent_dict = dict()
        for level in range(max_level + 1):
            node_list = [node for node in node_level if node_level[node] == level]
            for node in node_list:
                for edge in edges:
                    if edge[1] == node:
                        if node not in node_parent_dict:
                            node_parent_dict[node] = []
                        node_parent_dict[node].append((edge[0], node_level[edge[0]]))
        for key in node_parent_dict:
            node_parent_dict[key] = sorted(node_parent_dict[key],
                                           key=lambda x: (abs(node_level[key] - node_level[x[0]]), x[0]))
        return node_parent_dict

    def build_node_parent_dict_list(self, node_parent_dict):
        node_parent_dict_list = []
        common = {}
        temp = []
        temp_key = []
        for key in node_parent_dict:
            if len(node_parent_dict[key]) == 1:
                common[key] = node_parent_dict[key][0]
            else:
                temp_key.append(key)
                temp.append(node_parent_dict[key])
        permutations = list(itertools.product(*temp))
        for permutation in permutations:
            d = common.copy()
            for index in range(len(temp_key)):
                d[temp_key[index]] = permutation[index]
            node_parent_dict_list.append(d)
        return node_parent_dict_list

    def build_level_node(self, max_level, node_level, level_node, node_descendant, node_parent_dict, edges):
        cross_level_node_list = []
        for level in range(max_level + 1):
            if level - 1 not in level_node:
                node_list = [node for node in node_level if node_level[node] == level]
            else:
                node_list = []
                for parent in level_node[level - 1]:
                    for node in self.get_descendant(parent, level - 1, level, edges):
                        if node_level[node] == level and node not in node_list \
                                and parent == node_parent_dict[node][0][0]:
                            node_list.append(node)

                    temp_set = self.get_descendant(parent, level - 1, level, edges)
                    temp_set = temp_set.difference(set(node_list))
                    if parent in temp_set:
                        temp_set.remove(parent)
                    for node in temp_set:
                        if node_parent_dict[node][0][0] == parent:
                            cross_level_node_list.append(node)
                for node in cross_level_node_list:
                    if node_level[node] == level:
                        node_list.append(node)
                cross_level_node_list = [node for node in cross_level_node_list if node not in node_list]

            level_node[level] = node_list[:]
            """seen = set()
            seen_add = seen.add
            level_node[level] = [x for x in level_node[level] if not (x in seen or seen_add(x))]"""
            for node in node_list:
                node_descendant[node] = self.get_descendant(node, node_level[node], max_level, edges)
            del node_list[:]

    def rebuild_level_node(self, start_level, max_level, node_level, level_node, node_parent_dict, edges):
        for level in range(start_level, max_level + 1):
            level_node_list = []
            for parent in level_node[level - 1]:
                node_list = []
                temp = []
                for node in self.get_descendant(parent, level - 1, level, edges):
                    if node_level[node] == level and node not in level_node_list and parent == \
                            node_parent_dict[node][0][0]:
                        node_list.append(node)

                for index in range(len(level_node[level])):
                    temp = level_node[level][index:index + len(node_list)]
                    if set(temp) == set(node_list):
                        break
                level_node_list.extend(temp)
            for node in level_node[level]:
                if node not in level_node_list:
                    level_node_list.append(node)
            # print 'level = %d' % level
            # print 'old level_node[level]'
            # print level_node[level]
            level_node[level] = level_node_list[:]
            # print 'new level_node[level]'
            # print level_node[level]
            del level_node_list[:]

    def tree_layout(self, edges, node_level):
        level_node = dict()
        node_descendant = dict()
        max_level = 0
        for level in node_level.values():
            max_level = max(max_level, level)
        node_parent_dict = self.build_node_parent_dict(edges, node_level, max_level)
        print node_parent_dict
        print 'node_parent_dict'
        self.build_level_node(max_level, node_level, level_node, node_descendant, node_parent_dict, edges)
        for level in range(max_level + 1):
            if len(level_node[level]) > 1:
                top_node = level_node[level - 1][0]
                break
        # redo = True
        # while redo:
        # print level_node
        # print 'build_level_node finish'
        for level in range(1, max_level + 1):
            level_node_list = []
            for parent in level_node[level - 1]:
                temp = []
                for node in level_node[level]:
                    if node in self.get_descendant(parent, level - 1, level, edges) and node not in level_node_list \
                            and parent == node_parent_dict[node][0][0]:
                        temp.append(node)

                if len(temp) == 0:
                    continue
                level_node_list.extend(temp)
                # print 'inter switch_node_order'
                change = self.switch_node_order(temp, max_level, node_parent_dict, node_level, level_node, top_node,
                                                edges)
                """if change:
                    break
            if change:
                change = False
            else:
                redo = False"""

        node_x_position = self.tree_layout_x(level_node, node_descendant, node_parent_dict, edges)
        string = ''
        leaf_number = len([node for node in node_level if len(node_descendant[node]) == 0])
        print 'leaf_number = ' + str(leaf_number)
        weighted_coupling, unweighted_coupling = self.calculate_coupling(node_level.keys(), edges)
        with open('C:\wamp64\www\TSVisual\process_map\data\component01\config.json', 'r+') as f:
            for line in f:
                if 'width' in line:
                    string += '		"width"        : %d,\n' % (leaf_number * 300)
                elif 'height' in line:
                    string += '		"height"       : %d,\n' % ((max_level + 1) * 200)
                elif 'unweightedCoupling' in line:
                    string += '		"unweightedCoupling": %r,\n' % unweighted_coupling
                elif 'weightedCoupling' in line:
                    string += '		"weightedCoupling": %r,\n' % weighted_coupling
                else:
                    string += line
                if 'constraints' in line:
                    break
        with open('C:\wamp64\www\TSVisual\process_map\data\component01\config.json', 'w+') as f:
            f.write(string)
            # {"has":{"name":"doKeywordSearch"},"type":"position","x":0.7,"y":0.2,"weight":0.6},
            temp = ''
            y_step = float("{0:.8f}".format(1.0 / (max_level + 1)))
            y_start_position = 1.0 / (max_level + 2)
            for level in range(max_level + 1):
                for node in level_node[level]:
                    if node in node_x_position:
                        line = '\t\t{"has":{"name":"%s"},"type":"position","x":%.8f,"y":%.8f,"weight":0.6},' % (
                            node, node_x_position[node], y_start_position)
                    else:
                        line = '\t\t{"has":{"name":"%s"},"type":"position","y":%.8f,"weight":0.6},' % (
                            node, y_start_position)
                    temp += line + '\n'
                y_start_position += y_step
            f.write(temp)
            f.seek(-3, 1)
            f.write('\n\t]\n}')
        return level_node

    def get_leaf_node_count(self, descendant, edges):
        if len(descendant) == 0:
            return 1
        count = 0
        for node in descendant:
            is_leaf = True
            for edge in edges:
                if edge[0] == node:
                    is_leaf = False
                    break
            if is_leaf:
                count += 1
        return count

    def tree_layout_x(self, level_node, node_descendant, node_parent_dict, edges):
        max_level = max(level_node.keys())
        duration_dict = dict()  # key : node, value : dict(key : child node, value : (left, right))
        node_x_position = dict()
        node_x_position[level_node[0][0]] = 0.5
        for level in xrange(max_level):
            print 'level = %d' % level
            for node in level_node[level]:
                width = dict()
                total = 0
                duration_dict[node] = dict()
                child_node_list = [child_node for child_node in level_node[level + 1] if
                                   child_node in node_descendant[node] and node == node_parent_dict[child_node][0][0]]
                for child_node in self.get_descendant(node, level, max_level, edges):
                    if node_parent_dict[child_node][0][0] == node and child_node not in child_node_list:
                        child_node_list.append(child_node)
                if node in child_node_list:
                    child_node_list.remove(node)
                print 'node = %s    child_node_list' % node
                print child_node_list
                for child_node in child_node_list:
                    width[child_node] = self.get_leaf_node_count(node_descendant[child_node], edges)
                    total += width[child_node]
                duration = (0, 1) if level == 0 else duration_dict[node_parent_dict[node][0][0]][node]
                left, right = duration[0], duration[1]
                for child_node in child_node_list:
                    right = float(
                        "{0:.8f}".format(left + float(width[child_node]) / total * (duration[1] - duration[0])))
                    duration_dict[node][child_node] = (left, right)
                    print 'node = %s    duration = %r' % (child_node, (left, right))
                    node_x_position[child_node] = float("{0:.8f}".format((right + left) / 2))
                    left = right
        return node_x_position

    """def tree_layout_x(self, level_node, node_descendant, node_parent_dict, edges):
        node_x_position = dict()
        root = level_node[0][0]
        node_x_position[root] = 0.5
        node_x_position = self.tree_layout_x_recursive(root, 1, edges, level_node, (0.0, 1.0), node_descendant,
                                                       node_x_position, node_parent_dict)
        return node_x_position

    def tree_layout_x_recursive(self, root, level, edges, level_node, duration, node_descendant, node_x_position,
                                node_parent_dict):
        width = dict()
        current_level_nodes = [node for node in level_node[level] if
                               node in node_descendant[root] and root == node_parent_dict[node][0][0]]
        print 'current_level_nodes'
        print current_level_nodes
        duration_list = []
        total = 0
        for node in current_level_nodes:
            width[node] = self.get_leaf_node_count(node_descendant[node], edges)
            total += width[node]
        left, right = duration[0], duration[1]
        for node in current_level_nodes:
            right = float("{0:.8f}".format(left + float(width[node]) / total * (duration[1] - duration[0])))
            duration_list.append((left, right))
            node_x_position[node] = float("{0:.8f}".format((right + left) / 2))
            left = right
        for node in current_level_nodes:
            if len(node_descendant[node]) > 0:
                node_x_position = self.tree_layout_x_recursive(node, level + 1, edges, level_node,
                                                               duration_list[current_level_nodes.index(node)],
                                                               node_descendant, node_x_position, node_parent_dict)
        return node_x_position"""

    def switch_node_order(self, node_list, max_level, node_parent_dict, node_level, level_node, top_node, edges):
        total_cross = 0
        total_cross += self.calculate_cross(top_node, max_level, node_parent_dict, node_level, level_node, edges)
        # print 'calculate_cross finish'
        change = False
        redo = True
        while redo:
            swap = False
            for combinations in itertools.combinations(node_list, 2):
                level = node_level[node_list[0]]
                new_level_node = {}
                for key in level_node:
                    new_level_node[key] = level_node[key][:]
                index1, index2 = level_node[level].index(combinations[0]), level_node[level].index(
                    combinations[1])
                new_level_node[level][index1], new_level_node[level][index2] = level_node[level][index2], \
                                                                               level_node[level][index1]
                # print 'rebuild_level_node'
                self.rebuild_level_node(level + 1, max_level, node_level, new_level_node, node_parent_dict, edges)
                new_total_cross = 0
                new_total_cross += self.calculate_cross(top_node, max_level, node_parent_dict, node_level,
                                                        new_level_node, edges)
                if new_total_cross < total_cross:
                    total_cross = new_total_cross
                    level_node[level] = new_level_node[level][:]
                    self.rebuild_level_node(level + 1, max_level, node_level, level_node, node_parent_dict, edges)
                    new_level_node.clear()
                    swap = True
                    change = True
                    break
            if not swap:
                redo = False
        return change

    """def switch_node_order(self, node_list, node_level, edges, max_level, node_parent_dict, level_node, top_node):
        total_cross = 0
        total_cross += self.calculate_cross(top_node, edges, max_level, node_parent_dict, node_level, level_node)
        change = False
        redo = True
        while redo:
            swap = False
            for i in xrange(len(node_list)):
                for j in xrange(i + 1, len(node_list)):
                    level = node_level[node_list[0]]
                    new_level_node = {}
                    for key in level_node:
                        new_level_node[key] = level_node[key][:]
                    start_index = level_node[level].index(node_list[i])
                    temp = node_list[i]
                    new_level_node[level].remove(temp)
                    new_node_list = new_level_node[level][:start_index + j]
                    new_node_list.append(temp)
                    new_node_list.extend(new_level_node[level][start_index + j:])
                    new_level_node[level] = new_node_list[:]
                    self.rebuild_level_node(level + 1, max_level, node_level, new_level_node, edges, node_parent_dict)
                    new_total_cross = 0
                    new_total_cross += self.calculate_cross(top_node, edges, max_level, node_parent_dict, node_level,
                                                            new_level_node)

                    if new_total_cross < total_cross:
                        # print new_total_cross
                        total_cross = new_total_cross
                        node_list = new_node_list[:]
                        level_node[level] = new_level_node[level][:]
                        self.rebuild_level_node(level + 1, max_level, node_level, level_node, edges, node_parent_dict)
                        del new_node_list[:]
                        new_level_node.clear()
                        swap = True
                        change = True
                        break
                if swap:
                    break
            if not swap:
                redo = False
        return change"""

    def get_descendant(self, root, root_level, max_level, edges):
        next_level_node = [edge[1] for edge in edges if edge[0] == root]
        result = set()
        for node in next_level_node:
            result.add(node)
        temp = []
        for level in range(root_level + 2, max_level + 1):
            for node in next_level_node:
                for edge in edges:
                    if edge[0] == node:
                        temp.append(edge[1])
            for node in temp:
                result.add(node)
            next_level_node = temp[:]
            del temp[:]
        return result

    def calculate_cross(self, top_node, max_level, node_parent_dict, node_level, level_node, edges):
        cross = 0
        for level in range(node_level[top_node] + 1, max_level + 1):
            level_node_list = []
            for parent in level_node[level - 1]:
                node_list = []
                for node in level_node[level]:
                    if node in self.get_descendant(parent, level - 1, level, edges) and node not in level_node_list \
                            and parent == node_parent_dict[node][0][0]:
                        node_list.append(node)
                cross_list = []
                for node in node_list:
                    for edge in edges:
                        if edge[1] == node:
                            target_level = node_level[edge[0]]
                            target_node = edge[0]
                            current_node = node
                            while target_level != node_level[current_node]:
                                if target_level < node_level[current_node]:
                                    current_node = node_parent_dict[current_node][0][0]
                                else:
                                    target_node = node_parent_dict[target_node][0][0]
                                    target_level = node_level[target_node]
                            if target_node != current_node:
                                cross_list.append(edge)
                                cross += math.fabs(level_node[target_level].index(target_node) -
                                                   level_node[target_level].index(current_node))
                subcross = self.calculate_subcross(node_list, cross_list, node_level, level_node, node_parent_dict)
                cross += subcross
                level_node_list.extend(node_list)
        return cross

    def calculate_subcross(self, node_list, cross_list, node_level, level_node, node_parent_dict):
        size = len(node_list)
        if size == 1 or len(cross_list) == 0:
            return 0
        step = 2.0 / (size + 1)
        center = float(size - 1) / 2
        subcross_dict = dict()
        if size % 2 == 1:
            center = int(center)
            subcross_dict[node_list[center]] = 0
            for i, j in zip(xrange(center - 1, -1, -1), xrange(center + 1, size)):
                subcross_dict[node_list[i]] = (i - center) * step
                subcross_dict[node_list[j]] = (j - center) * step
        else:
            for i, j in zip(xrange(int(center - 0.5), -1, -1), xrange(int(center + 0.5), size)):
                subcross_dict[node_list[i]] = (i - center) * step
                subcross_dict[node_list[j]] = (j - center) * step
        subcross = 0.0
        for edge in cross_list:
            temp, node = edge
            parent = node_parent_dict[node][0]
            while parent[1] != node_level[temp]:
                parent = node_parent_dict[parent[0]][0]
            current_list = level_node[node_level[temp]]
            if current_list.index(temp) < current_list.index(parent[0]):
                subcross += subcross_dict[node]
            else:
                subcross -= subcross_dict[node]
        return subcross
