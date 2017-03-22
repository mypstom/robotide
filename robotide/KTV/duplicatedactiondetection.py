import robotide

import time
import os
import itertools
from robotide.publish import DuplicateDetection


class DuplicatedActionDetection:
    token = '%$&*$#@'
    threshold = 5
    use_hash = True
    hash_table = {}

    def Excute(self, datafiles, filepath):
        pass

    def build_table(self, all_step_list):
        for item in all_step_list:
            if self.token in item:
                continue
            if item not in self.hash_table:
                self.hash_table[item] = unichr(abs(hash(item)) % 65536)


class LongestCommonSubsequence(DuplicatedActionDetection):
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

    def Excute(self, datafiles, filepath):
        source = os.path.abspath(filepath)
        # self.DetectionBetweenUKandUK(datafiles)
        # self.DetectionBetweenTCandTC(datafiles)
        self.DetectionAllScript(datafiles, source)
        DuplicateDetection(controller=datafiles).publish()

    def DetectionAllScript(self, datafiles, source):
        steps_list = []
        result_list = []

        for df in datafiles:
            for test_case in df.tests:
                steps_list.append(self.get_step_list(test_case.steps))
            for user_keyword in df.keywords:
                steps_list.append(self.get_step_list(user_keyword.steps))

        if self.use_hash:
            temp = []
            for steps in steps_list:
                temp.extend(steps)
            self.build_table(temp)
            steps_list = [[self.hash_table[step] for step in steps] for steps in steps_list]

        for combinations in itertools.combinations(steps_list, 2):
            temp = self.LCS(combinations[0], combinations[1])[0]
            if len(temp) >= self.threshold:
                result_list.append(temp)

        result_list.sort(key=lambda x: len(x))
        result_list.reverse()
        #print result_list
        with open(source + '\ScriptDuplicated.txt', 'w+') as f:
            for result in result_list:
                if len(result) == 0:
                    continue
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

    def find_duplicated_position(self, datafiles, result, f):
        for df in datafiles:
            for test_case in df.tests:
                step_list = self.get_step_list(test_case.steps)
                self.find_position_and_write_file(step_list, result, f, 'TC', test_case.name)
            for user_keyword in df.keywords:
                step_list = self.get_step_list(user_keyword.steps)
                self.find_position_and_write_file(step_list, result, f, 'UK', user_keyword.name)

    def find_position_and_write_file(self, step_list, result, f, _type, name):
        temp = []
        index = 0
        match = False
        i = 0
        # print result
        # print step_list
        while i < len(step_list):
            # print 'i = %d index = %d' %(i,index)
            if step_list[i] == result[index]:
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
                f.write(_type + ':' + name + '\n')
                for x, y in temp:
                    f.write(str(x + 1) + ' ~ ' + str(y + 1) + ',')
                f.seek(-1, 1)
                f.write(' action duplicated\n')
                i = temp[0][0]
                index = 0
                del temp[:]
            i += 1

    def get_step_list(self, steps):
        result = []
        for step in steps:
            if type(step) is robotide.controller.stepcontrollers.ForLoopStepController:
                result.append('Loop')
            else:
                result.append(step.keyword)
        return result

    """def DetectionBetweenUKandUK(self, datafiles):
        f = open('UK2UKduplicated-LCS.txt', 'w+')
        for df in datafiles:
            i = 0
            length = len(df.keywords)
            while i < length - 1:
                userKeywordsListFirstList = list()
                for step in df.keywords[i].steps:
                    if type(step) is robotide.controller.stepcontrollers.ForLoopStepController:
                        userKeywordsListFirstList.append('Loop')
                    else:
                        userKeywordsListFirstList.append(step.keyword)
                j = i + 1
                while j < length:
                    userKeywordsListSecondList = list()
                    for step in df.keywords[j].steps:
                        if type(step) is robotide.controller.stepcontrollers.ForLoopStepController:
                            userKeywordsListSecondList.append('Loop')
                        else:
                            userKeywordsListSecondList.append(step.keyword)
                    result = list()
                    result = self.LCS(userKeywordsListFirstList, userKeywordsListSecondList)
                    f.write(df.keywords[i].display_name)
                    f.write(' , ')
                    f.write(df.keywords[j].display_name)
                    f.write('\n')
                    f.write('len(lcs) = ')
                    f.write(str(len(result[0])))
                    f.write('\n')
                    f.write('len(result) = ')
                    f.write(str(len(result)))
                    f.write('\n')
                    for lcs in result:
                        f.write('lcs = [')
                        for item in lcs:
                            f.write(str(item).encode('utf-8'))
                            f.write(' , ')
                        f.write(']\n\n')
                    j += 1
                i += 1

        f.close()

    def DetectionBetweenTCandTC(self, datafiles):
        f = open('TC2TCduplicated-LCS.txt', 'w+')
        for df in datafiles:
            i = 0
            length = len(df.tests)
            while i < length - 1:
                testCaseListFirstList = list()
                for step in df.tests[i].steps:
                    if type(step) is robotide.controller.stepcontrollers.ForLoopStepController:
                        testCaseListFirstList.append('Loop')
                    else:
                        testCaseListFirstList.append(step.keyword)
                j = i + 1
                while j < length:
                    testCaseListSecondList = list()
                    for step in df.tests[j].steps:
                        if type(step) is robotide.controller.stepcontrollers.ForLoopStepController:
                            testCaseListSecondList.append('Loop')
                        else:
                            testCaseListSecondList.append(step.keyword)
                    result = list()
                    result = self.LCS(testCaseListFirstList, testCaseListSecondList)
                    f.write(df.tests[i].display_name)
                    f.write(' , ')
                    f.write(df.tests[j].display_name)
                    f.write('\n')
                    f.write('len(lcs) = ')
                    f.write(str(len(result[0])))
                    f.write('\n')
                    f.write('len(result) = ')
                    f.write(str(len(result)))
                    f.write('\n')
                    for lcs in result:
                        f.write('lcs = [')
                        for item in lcs:
                            f.write(str(item).encode('utf-8'))
                            f.write(' , ')
                        f.write(']\n\n')
                    j += 1
                i += 1

        f.close()"""


class LongestRepeatedSubstring(DuplicatedActionDetection):
    def Excute(self, datafiles, filepath):
        source = os.path.abspath(filepath)
        self.DetectionAllScript(datafiles, source)
        DuplicateDetection(controller=datafiles).publish()

    def DetectionAllScript(self, datafiles, source):
        token_count = 1
        f = open(source + '\ScriptDuplicated.txt', 'w+')
        count = 1
        all_step_list = list()
        for df in datafiles:
            for testcase in df.tests:
                for step in testcase.steps:
                    if type(step) is robotide.controller.stepcontrollers.ForLoopStepController:
                        all_step_list.append('Loop')
                    else:
                        all_step_list.append(str(step.keyword))
                all_step_list.append(self.token + str(token_count))
                token_count += 1
            for userKeyword in df.keywords:
                for step in userKeyword.steps:
                    if type(step) is robotide.controller.stepcontrollers.ForLoopStepController:
                        all_step_list.append('Loop')
                    else:
                        all_step_list.append(str(step.keyword))
                all_step_list.append(self.token + str(token_count))
                token_count += 1

        if self.use_hash:
            self.build_table(all_step_list)

        while True:
            string = ''
            for item in all_step_list:
                if self.token in item:
                    string += item
                else:
                    string += self.hash_table[item] if self.use_hash else item
                    # string += item
                string += ','
            string = string[:len(string) - 1]
            start_time = time.time()
            result = self.maxRepeatedSubstring(string)
            elapsed_time = time.time() - start_time
            f.write(str(count))
            f.write(' time LRS\t')
            f.write('elapsed_time = ')
            f.write(str(elapsed_time))
            f.write('\n')
            if result is not None:
                # print result
                is_finish, all_step_list = self.FindLRSResultPosition(result, all_step_list, datafiles, f)
                if is_finish:
                    f.write('duplicated action length smaller than threshold\n')
                    break
                f.write('\n\n')
            else:
                f.write('no duplicated actions be detected\n')
                break
            count += 1
        f.close()

    def FindLRSResultPosition(self, result_string, all_step_list, datafiles, f):
        lrs_list = result_string.strip(',').split(',')
        result = list()
        for lrs in lrs_list:
            if self.token in lrs:
                continue
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

        string = 'resultList = ['
        for item in result:
            string += item
            string += ','
        string = string[:len(string) - 1] + ']'
        f.write(string)
        f.write('\n')

        for df in datafiles:
            for test_case in df.tests:
                region_list = []
                for i in xrange(len(test_case.steps)):
                    if test_case.steps[i].keyword == result[0] and i + len(result) <= len(test_case.steps):
                        temp = [test_case.steps[i + j].keyword for j in xrange(len(result))]
                        if temp == result:
                            region_list.append(i)
                for start in region_list:
                    f.write('TC:' + str(test_case.name) + '\n')
                    f.write(str(start + 1) + ' ~ ' + str(start + len(result)) + ' action duplicated\n')

                del region_list[:]
                self.rebuild_all_step_list(result, all_step_list)
            for user_keyword in df.keywords:
                region_list = []
                for i in xrange(len(user_keyword.steps)):
                    if user_keyword.steps[i].keyword == result[0] and i + len(result) <= len(user_keyword.steps):
                        temp = [user_keyword.steps[i + j].keyword for j in xrange(len(result))]
                        if temp == result:
                            region_list.append(i)
                for start in region_list:
                    f.write('UK:' + str(user_keyword.name) + '\n')
                    f.write(str(start + 1) + ' ~ ' + str(start + len(result)) + ' action duplicated\n')

                del region_list[:]
                self.rebuild_all_step_list(result, all_step_list)

        f.write('\n')

        # print 'after'
        # print all_step_list

        return False, all_step_list

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

    def maxRepeatedSubstring(self, repeatedString):  # get longestSubString from string
        maxSubstringLength = len(repeatedString) - 1
        while maxSubstringLength > 0:
            startPoint = 0
            while startPoint + maxSubstringLength <= len(repeatedString):
                substringToMatch = repeatedString[startPoint:startPoint + maxSubstringLength]
                if substringToMatch in repeatedString[startPoint + 1:]:
                    return substringToMatch
                startPoint += 1
            maxSubstringLength -= 1
        return None

    def longest_substr(self, lst):  # find longestSubString from item in list
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
        return lrs
