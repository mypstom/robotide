import robotide

import time
import os


class DuplicatedActionDetection:
    def Excute(self, datafiles):
        pass


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

    def Excute(self, datafiles):
        self.DetectionBetweenUKandUK(datafiles)
        self.DetectionBetweenTCandTC(datafiles)

    def DetectionBetweenUKandUK(self, datafiles):
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

        f.close()


class LongestRepeatedSubstring(DuplicatedActionDetection):
    def Excute(self, datafiles):
        # self.DetectionBetweenUKandUK(datafiles)
        # self.DetectionBetweenTCandTC(datafiles)
        self.DetectionAllScript(datafiles)

    def DetectionAllScript(self, datafiles):
        f = open('ScriptDuplicated-LRS.txt', 'w+')
        count = 1
        allStepList = list()
        for df in datafiles:
            for testcase in df.tests:
                for step in testcase.steps:
                    if type(step) is robotide.controller.stepcontrollers.ForLoopStepController:
                        allStepList.append('Loop')
                    else:
                        allStepList.append(str(step.keyword))
            for userKeyword in df.keywords:
                for step in userKeyword.steps:
                    if type(step) is robotide.controller.stepcontrollers.ForLoopStepController:
                        allStepList.append('Loop')
                    else:
                        allStepList.append(str(step.keyword))
        """string = '['
        for item in lst:
            string += str(item)
            string += ','
        string = string[:len(string) - 1] + ']'
        f.write(string)
        f.write('\n\n')"""
        while len(allStepList) > 0:
            print 'len(allStepList)= %s ' % (len(allStepList))
            string = ''
            for item in allStepList:
                string += item
                string += ','
            string = string[:len(string) - 1]
            # print 'string = %s' % (string)
            # tempList = list()
            # tempList.append(string)
            start_time = time.time()
            result = self.maxRepeatedSubstring(string)
            elapsed_time = time.time() - start_time
            print 'LRS elapsed_time = %s' % elapsed_time
            print '%s times' % count
            f.write(str(count))
            f.write(' time LRS\t')
            f.write('elapsed_time = ')
            f.write(str(elapsed_time))
            f.write('\n')
            if result is not None:
                print 'result = %s' % result
                f.write(result)
                f.write('\n\n')

                lrsList = result.split(',')
                isKeyword = False
                for lrs in lrsList:
                    print 'lrs = %s' % lrs
                    for item in allStepList:
                        if item == lrs:
                            isKeyword = True

                    allStepList = [item for item in allStepList if item != lrs]
                print 'len(allStepList)= %s' % len(allStepList)
                if not isKeyword:
                    break
            else:
                break
            count += 1
        f.write('len(leave step) = ')
        f.write(str(len(allStepList)))
        f.write('\nleave step = [')
        for item in allStepList:
            f.write(item)
            f.write(',')
        f.seek(-1, os.SEEK_CUR)
        f.write(']')
        f.close()

    def DetectionBetweenUKandUK(self, datafiles):
        f = open('UK2UKduplicated-LRS.txt', 'w+')
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
                    lrs = self.LongestRepeatedSubstring(userKeywordsListFirstList, userKeywordsListSecondList)
                    f.write(df.keywords[i].display_name)
                    f.write(' , ')
                    f.write(df.keywords[j].display_name)
                    f.write('\n')
                    f.write('lrs = ')
                    if lrs is not None:
                        f.write(str(lrs))
                    f.write('\n\n')
                    j += 1
                i += 1

        f.close()

    def DetectionBetweenTCandTC(self, datafiles):
        f = open('TC2TCduplicated-LRS.txt', 'w+')
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
                    lrs = self.LongestRepeatedSubstring(testCaseListFirstList, testCaseListSecondList)
                    f.write(df.tests[i].display_name)
                    f.write(' , ')
                    f.write(df.tests[j].display_name)
                    f.write('\n')
                    f.write('lrs = ')
                    if lrs is not None:
                        f.write(str(lrs))
                    f.write('\n\n')
                    j += 1
                i += 1

        f.close()

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
        # string1 = ''.join(list1)
        # string2 = ''.join(list2)
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
        # print 'string1 = %s , string2 = %s' % (string1, string2)
        lst = list()
        lst.append(string1)
        lst.append(string2)
        lrs = self.longest_substr(lst)
        # print '\nlrs = %s\n' %(lrs)
        return lrs
