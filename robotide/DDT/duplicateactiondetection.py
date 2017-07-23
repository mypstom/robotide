import time
import os
import itertools
from robotide.publish import DuplicateDetection
from robotide.controller.stepcontrollers import ForLoopStepController


class DuplicateActionDetection:
    token = '%$&*$#@'
    threshold = 3
    use_hash = True
    hash_table = {}
    comment_list = []
    duplicate_lines = 0
    steps_list = None

    def __init__(self, threshold):
        self.threshold = threshold

    def execute(self, datafiles, file_path):
        source = os.path.abspath(file_path)
        self.check_step_have_keyword(datafiles)
        self.detect_all_script(datafiles, source)
        self.uncommend_steps()
        DuplicateDetection(controller=datafiles).publish()

    def detect_all_script(self, datafiles, source):
        pass

    def build_steps_list(self, datafiles):
        if self.steps_list is None:
            self.steps_list = []
        del self.steps_list[:]
        self._build_steps_list(datafiles)

    def _build_steps_list(self, datafiles):
        for df in datafiles:
            for test_case in df.tests:
                self.steps_list.append(self._get_step_list(test_case.steps))
            for user_keyword in df.keywords:
                self.steps_list.append(self._get_step_list(user_keyword.steps))

        if self.use_hash:
            temp = []
            for steps in self.steps_list:
                temp.extend(steps)
            temp = [item for item in temp]
            self.build_table(temp)
            self.steps_list = [[(step, 0) for step in steps] for steps in self.steps_list]

    def _check_step_duplicated(self, index, duplicated_step_set):
        count = 0
        step_list = self.steps_list[index]
        for i in duplicated_step_set:
            if step_list[i][1] == 0:
                count += 1
        return count

    def _set_step_duplicated(self, index, duplicated_step_set, flag):
        step_list = self.steps_list[index]
        for i in duplicated_step_set:
            if step_list[i][1] == 0:
                step_list[i] = (step_list[i][0], flag)
            elif step_list[i][1] == 1:
                step_list[i] = (step_list[i][0], flag)

    def _get_step_list(self, steps):
        result = []
        for step in steps:
            if type(step) is ForLoopStepController:
                result.append('Loop')
            else:
                result.append(step.keyword)
        return result

    def check_step_have_keyword(self, datafiles):
        user_keyword_count = 0
        for df in datafiles:
            for test_case in df.tests:
                for step in test_case.steps:
                    if type(step) is not ForLoopStepController and step.keyword is None:
                        self.comment_list.append(step)
                        step.comment()
            user_keyword_count += len(df.keywords)
            for user_keyword in df.keywords:
                for step in user_keyword.steps:
                    if type(step) is not ForLoopStepController and step.keyword is None:
                        self.comment_list.append(step)
                        step.comment()
        print 'user_keyword_count = %d' % user_keyword_count

    def uncommend_steps(self):
        for step in self.comment_list:
            step.uncomment()
        del self.comment_list[:]

    def build_table(self, all_step_list):
        for item in all_step_list:
            if item not in self.hash_table:
                self.hash_table[item] = unichr(abs(hash(item)) % 65536)

    def write_steps_file(self, source):
        index = 1
        with open(source + '\Steps1.txt', 'w+') as f:
            for steps in self.steps_list:
                for step in steps:
                    if step[1] == 0:
                        f.write(str(index) + '\t' + '0\n')
                    else:
                        f.write(str(index) + '\t' + '1\n')
                    index += 1
        index = 1
        with open(source + '\Steps2.txt', 'w+') as f:
            for steps in self.steps_list:
                for step in steps:
                    if step[1] != 2:
                        f.write(str(index) + '\t' + '0\n')
                    else:
                        f.write(str(index) + '\t' + '1\n')
                    index += 1


class LongestCommonSubsequence(DuplicateActionDetection):
    def lcs_mat(self, list1, list2):
        m = len(list1)
        n = len(list2)
        # construct the matrix, of all zeroes
        mat = [[0] * (n + 1) for row in range(m + 1)]
        # populate the matrix, iteratively
        for row in range(1, m + 1):
            for col in range(1, n + 1):
                if list1[row - 1] == list2[col - 1]:
                    # if it's the same element, it's one longer than the LCS of the truncated lists
                    mat[row][col] = mat[row - 1][col - 1] + 1
                else:
                    # they're not the same, so it's the the maximum of the lengths of the LCSs of the two options (different list truncated in each case)
                    mat[row][col] = max(mat[row][col - 1], mat[row - 1][col])
        # the matrix is complete
        return mat

    def all_lcs(self, lcs_dict, mat, list1, list2, index1, index2):
        # if we've calculated it already, just return that
        if (lcs_dict.has_key((index1, index2))): return lcs_dict[(index1, index2)]
        # otherwise, calculate it recursively
        if (index1 == 0) or (index2 == 0):  # base case
            return [[]]
        elif list1[index1 - 1] == list2[index2 - 1]:
            # elements are equal! Add it to all LCSs that pass through these indices
            lcs_dict[(index1, index2)] = [prevs + [list1[index1 - 1]] for prevs in
                                          self.all_lcs(lcs_dict, mat, list1, list2, index1 - 1, index2 - 1)]
            return lcs_dict[(index1, index2)]
        else:
            lcs_list = []  # set of sets of LCSs from here
            # not the same, so follow longer path recursively
            if mat[index1][index2 - 1] >= mat[index1 - 1][index2]:
                before = self.all_lcs(lcs_dict, mat, list1, list2, index1, index2 - 1)
                for series in before:  # iterate through all those before
                    if not series in lcs_list: lcs_list.append(
                        series)  # and if it's not already been found, append to lcs_list
            if mat[index1 - 1][index2] >= mat[index1][index2 - 1]:
                before = self.all_lcs(lcs_dict, mat, list1, list2, index1 - 1, index2)
                for series in before:
                    if not series in lcs_list: lcs_list.append(series)
            lcs_dict[(index1, index2)] = lcs_list
            return lcs_list

    def LCS(self, list1, list2):
        # mapping of indices to list of LCSs, so we can cut down recursive calls enormously
        mapping = dict()
        # start the process...
        return self.all_lcs(mapping, self.lcs_mat(list1, list2), list1, list2, len(list1), len(list2))

    def detect_all_script(self, datafiles, source):
        self.build_steps_list(datafiles)
        result_list = []
        f = open(source + '\ScriptDuplicated.txt', 'w+')

        steps_list = [[self.hash_table[step[0]] for step in steps if step[1] == 0 and step[0] != 'Comment'] for steps in
                      self.steps_list]
        for combinations in itertools.combinations(steps_list, 2):
            temp = self.LCS(combinations[0], combinations[1])[0]
            if len(temp) >= self.threshold:
                result_list.append(temp)

        result_list.sort(key=lambda x: len(x))
        result_list.reverse()
        for result in result_list:
            if self.use_hash:
                result = [self.hash_table.keys()[self.hash_table.values().index(item)] for item in result]
            string = 'resultList = ['
            for item in result:
                string += item
                string += ','
            string = string[:len(string) - 1] + ']'
            f.write(string)
            f.write('\n')
            self.find_duplicated_position(datafiles, result, f)
            f.write('\n')
        self.compute_duplicate_lines()
        f.write('duplicated lines = %d\n' % self.duplicate_lines)
        self.write_steps_file(source)
        f.close()

    def find_duplicated_position(self, datafiles, result, f):
        index = 0
        duplicate_lines = 0
        is_first_duplicate_node = True
        for df in datafiles:
            for test_case in df.tests:
                is_first_duplicate_node, temp = self.find_position_and_write_file(index, result, f, 'TC',
                                                                                  test_case.name,
                                                                                  is_first_duplicate_node)
                duplicate_lines += temp
                index += 1
            for user_keyword in df.keywords:
                is_first_duplicate_node, temp = self.find_position_and_write_file(index, result, f, 'UK',
                                                                                  user_keyword.name,
                                                                                  is_first_duplicate_node)
                duplicate_lines += temp
                index += 1
        self.duplicate_lines += duplicate_lines
        if duplicate_lines >= len(result):
            self.duplicate_lines -= len(result)

    def find_position_and_write_file(self, steps_index, result, f, type_name, name, is_first_duplicate_node):
        temp = []
        index = 0
        match = False
        i = 0
        duplicated_step_set = set()
        step_list = self.steps_list[steps_index]
        duplicated_lines = 0
        while i < len(step_list):
            if step_list[i][0] == result[index]:
                if not match:
                    start = i
                    match = True
                index += 1
            else:
                if match:
                    end = i - 1
                    temp.append((start, end))
                    match = False
            if index == len(result):
                end = i
                temp.append((start, end))
                match = False
                f.write(type_name + ':' + name + '\n')
                for x, y in temp:
                    f.write(str(x + 1) + ' ~ ' + str(y + 1) + ', ')
                    for j in xrange(x, y + 1):
                        duplicated_step_set.add(j)
                f.seek(-2, 1)
                f.write(' action duplicated\n')
                i = temp[0][0]
                index = 0
                del temp[:]
                if is_first_duplicate_node:
                    temp_lines = self._check_step_duplicated(steps_index, duplicated_step_set)
                    if temp_lines == len(result):
                        duplicated_lines += temp_lines
                        self._set_step_duplicated(steps_index, duplicated_step_set, 1)
                        is_first_duplicate_node = False
                else:
                    temp_lines = self._check_step_duplicated(steps_index, duplicated_step_set)
                    if temp_lines == len(result):
                        duplicated_lines += temp_lines
                        self._set_step_duplicated(steps_index, duplicated_step_set, 2)
                duplicated_step_set.clear()
            i += 1
        return is_first_duplicate_node, duplicated_lines

    def compute_duplicate_lines(self):
        count = 0
        for steps in self.steps_list:
            for step in steps:
                if step[1] != 0:
                    count += 1


class LongestRepeatedSubstring(DuplicateActionDetection):
    def detect_all_script(self, datafiles, source):
        self.build_steps_list(datafiles)
        token_count = 1
        f = open(source + '\ScriptDuplicated.txt', 'w+')
        count = 1
        all_step_list = list()
        for df in datafiles:
            for testcase in df.tests:
                for step in testcase.steps:
                    if type(step) is ForLoopStepController:
                        all_step_list.append('Loop')
                    else:
                        all_step_list.append(step.keyword)
                all_step_list.append(self.token + str(token_count))
                token_count += 1
            for userKeyword in df.keywords:
                for step in userKeyword.steps:
                    if type(step) is ForLoopStepController:
                        all_step_list.append('Loop')
                    else:
                        all_step_list.append(step.keyword)
                all_step_list.append(self.token + str(token_count))
                token_count += 1

        while 'Comment' in all_step_list:  # remove all Comment step
            all_step_list.remove('Comment')

        if self.use_hash:
            self.build_table(all_step_list)

        while True:
            string = ''
            for item in all_step_list:
                string += self.hash_table[item] if self.use_hash else item
                string += ','
            string = string[:len(string) - 1]
            start_time = time.time()
            result = self.max_non_overlapping_repeated_substring(string)
            elapsed_time = time.time() - start_time
            f.write(str(count))
            f.write(' time LRS\t')
            f.write('elapsed_time = ')
            f.write(str(elapsed_time))
            f.write('\n')
            if result is not None:
                is_finish, all_step_list = self.FindLRSResultPosition(result, all_step_list, datafiles, f)
                if is_finish:
                    f.write('duplicated action length smaller than threshold\n')
                    break
                f.write('\n\n')
            else:
                f.write('no duplicated actions be detected\n')
                break
            count += 1
            # break
        f.write('duplicated lines = %d\n' % self.duplicate_lines)
        self.write_steps_file(source)
        f.close()

    def FindLRSResultPosition(self, result_string, all_step_list, datafiles, f):
        lrs_list = result_string.strip(',').split(',')
        result = list()
        for lrs in lrs_list:
            if self.use_hash:
                for item in all_step_list:
                    if item in self.hash_table and self.hash_table[item] == lrs:
                        result.append(item)
                        break
            else:
                if lrs in all_step_list:
                    result.append(lrs)

        if len(result) < self.threshold:
            return True, all_step_list

        # print result
        string = 'resultList = ['
        for item in result:
            string += item
            string += ','
        string = string[:len(string) - 1] + ']'
        f.write(string)
        f.write('\n')

        node_count = 0
        steps_index = 0
        duplicate_lines = 0
        duplicated_step_set = set()
        is_first_duplicate_node = True
        for df in datafiles:
            for test_case in df.tests:
                duplicated_step_set.clear()
                region_list = self.find_duplicated_region(test_case, result)
                for region in region_list:
                    node_count += 1
                    # s = ''
                    f.write('TC:' + str(test_case.name) + '\n')
                    # s += 'TC:' + str(test_case.name) + '\n'
                    for start, end in region:
                        f.write(str(start + 1) + ' ~ ' + str(end + 1) + ', ')
                        # s += str(start + 1) + ' ~ ' + str(end + 1) + ', '
                        for j in xrange(start, end + 1):
                            duplicated_step_set.add(j)
                    f.seek(-2, 1)
                    # s = s[:len(s) - 2]
                    f.write(' action duplicated\n')
                    if is_first_duplicate_node:
                        temp = self._check_step_duplicated(steps_index, duplicated_step_set)
                        if temp == len(result):
                            duplicate_lines += temp
                            self._set_step_duplicated(steps_index, duplicated_step_set, 1)
                            # print s + '\t' + str(temp)
                            is_first_duplicate_node = False
                    else:
                        temp = self._check_step_duplicated(steps_index, duplicated_step_set)
                        if temp == len(result):
                            duplicate_lines += temp
                            self._set_step_duplicated(steps_index, duplicated_step_set, 2)
                            # print s + '\t' + str(temp)
                    duplicated_step_set.clear()
                del region_list[:]
                self.rebuild_all_step_list(result, all_step_list)
                steps_index += 1
            for user_keyword in df.keywords:
                duplicated_step_set.clear()
                region_list = self.find_duplicated_region(user_keyword, result)
                for region in region_list:
                    node_count += 1
                    # s = ''
                    f.write('UK:' + str(user_keyword.name) + '\n')
                    # s += 'UK:' + str(user_keyword.name) + '\n'
                    for start, end in region:
                        f.write(str(start + 1) + ' ~ ' + str(end + 1) + ', ')
                        # s += str(start + 1) + ' ~ ' + str(end + 1) + ', '
                        for j in xrange(start, end + 1):
                            duplicated_step_set.add(j)
                    f.seek(-2, 1)
                    # s = s[:len(s) - 2]
                    f.write(' action duplicated\n')
                    if is_first_duplicate_node:
                        temp = self._check_step_duplicated(steps_index, duplicated_step_set)
                        if temp == len(result):
                            duplicate_lines += temp
                            self._set_step_duplicated(steps_index, duplicated_step_set, 1)
                            # print s + '\t' + str(temp)
                            is_first_duplicate_node = False
                    else:
                        temp = self._check_step_duplicated(steps_index, duplicated_step_set)
                        if temp == len(result):
                            duplicate_lines += temp
                            self._set_step_duplicated(steps_index, duplicated_step_set, 2)
                            # print s + '\t' + str(temp)
                    duplicated_step_set.clear()
                del region_list[:]
                self.rebuild_all_step_list(result, all_step_list)
                steps_index += 1
        f.write('\n')
        # self.duplicate_lines += (node_count - 1) * len(result)
        self.duplicate_lines += duplicate_lines
        if duplicate_lines >= len(result):
            self.duplicate_lines -= len(result)

        return False, all_step_list

    def find_duplicated_region(self, controller, result):
        region_list = []
        step_index = 0
        while step_index < len(controller.steps):
            temp = []
            temp_index = step_index
            indexes = []
            start = None
            while len(temp) < len(result) and temp_index < len(controller.steps):
                if isinstance(controller.steps[temp_index], ForLoopStepController):
                    temp.append('Loop')
                    if start is None:
                        start = temp_index
                elif controller.steps[temp_index].keyword == 'Comment':
                    if start is not None:
                        indexes.append((start, temp_index - 1))
                        start = None
                else:
                    temp.append(controller.steps[temp_index].keyword)
                    if start is None:
                        start = temp_index
                temp_index += 1

            if len(temp) == len(result) and start is not None:
                indexes.append((start, temp_index - 1))
            if temp == result:
                region_list.append(indexes)
                step_index = indexes[len(indexes) - 1][1]
            step_index += 1
        return region_list

    """def find_duplicated_region(self, controller, result):
        region_list = []
        step_index = 0
        while step_index < len(controller.steps):
            if isinstance(controller.steps[step_index], ForLoopStepController):
                if 'Loop' == result[0] and step_index + len(result) <= len(controller.steps):
                    # temp = [test_case.steps[i + j].keyword for j in xrange(len(result))]
                    temp = []
                    for j in xrange(len(result)):
                        if isinstance(controller.steps[step_index + j], ForLoopStepController):
                            temp.append('Loop')
                        else:
                            temp.append(controller.steps[step_index + j].keyword)
                    if temp == result:
                        region_list.append(step_index)
                        step_index += len(result)
            else:
                if controller.steps[step_index].keyword == result[0] and step_index + len(result) <= len(controller.steps):
                    # temp = [test_case.steps[i + j].keyword for j in xrange(len(result))]
                    temp = []
                    for j in xrange(len(result)):
                        if isinstance(controller.steps[step_index + j], ForLoopStepController):
                            temp.append('Loop')
                        else:
                            temp.append(controller.steps[step_index + j].keyword)
                    if temp == result:
                        region_list.append(step_index)
                        step_index += len(result)
            step_index += 1
        return region_list"""

    def rebuild_all_step_list(self, result, all_step_list):
        remove_set = set()
        for i in xrange(len(all_step_list)):
            if all_step_list[i] == result[0] and i + len(result) <= len(all_step_list):
                temp = all_step_list[i:i + len(result)]
                if temp == result:
                    for j in xrange(len(result)):
                        remove_set.add(i + j)
        for index in reversed(sorted(remove_set)):  # because del will change the index
            del all_step_list[index]

    def max_non_overlapping_repeated_substring(self, repeated_string):  # get longestSubString from string
        maxSubstringLength = len(repeated_string) / 2
        while maxSubstringLength > 0:
            startPoint = 0
            while startPoint + maxSubstringLength <= len(repeated_string):
                substringToMatch = repeated_string[startPoint:startPoint + maxSubstringLength]
                if substringToMatch in repeated_string[startPoint + maxSubstringLength:]:
                    return substringToMatch
                startPoint += 1
            maxSubstringLength -= 1
        return None

    """def maxRepeatedSubstring(self, repeatedString):  # get longestSubString from string
        maxSubstringLength = len(repeatedString) - 1
        while maxSubstringLength > 0:
            startPoint = 0
            while startPoint + maxSubstringLength <= len(repeatedString):
                substringToMatch = repeatedString[startPoint:startPoint + maxSubstringLength]
                if substringToMatch in repeatedString[startPoint + 1:]:
                    return substringToMatch
                startPoint += 1
            maxSubstringLength -= 1
        return None"""

    """def longest_substr(self, lst):  # find longestSubString from item in list
        longest = None
        for word in lst:
            for i in range(len(word)):
                for j in range(i + 1, len(word) + 1):
                    if ((longest is None or (j - i > len(longest))) and
                                sum(word[i:j] in w for w in lst) > 1):
                        longest = word[i:j]
        return longest

    def LongestRepeatedSubstring(self, list1, list2):
        string1 = ''
        for item in list1:
            string1 += item
            string1 += ','
        string1 = string1[:len(string1) - 1]
        string2 = ''
        for item in list2:
            string2 += item
            string2 += ','
        string2 = string2[:len(string2) - 1]
        lst = list()
        lst.append(string1)
        lst.append(string2)
        lrs = self.longest_substr(lst)
        return lrs"""
