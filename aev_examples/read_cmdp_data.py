import dill
import os
import sys
sys.path.append(os.path.abspath("../CMDP"))
import CMDP.consMDP
import psutil


class cmdp_info:
    def __init__(self, file_name, capacity):

        self.cmdp, self.targets = self.read_cmdp_dill_file(file_name, capacity)
        self.cap = capacity

        self.SF = self.cmdp.get_safe(self.cap)

        self.SFR = self.cmdp.get_positiveReachability(self.targets, self.cap)

        self.SFRR = self.cmdp.get_Buchi(self.targets, self.cap)




    def read_cmdp_dill_file(self,file_name, capacity):
        f = open(file_name, 'rb')

        cmdp = dill.load(f)
        targets = dill.load(f)

        return cmdp, targets