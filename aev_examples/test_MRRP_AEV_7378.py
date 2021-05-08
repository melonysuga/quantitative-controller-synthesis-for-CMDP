import os
import sys
current_directory = os.path.dirname(os.path.abspath("test_MRRP_AEV_7378.py"))
root_path = os.path.abspath(os.path.dirname(current_directory) + os.path.sep + ".")
sys.path.append(root_path)
import aev_examples.read_cmdp_data
import time
from MRRP.MRRP_calculate import MRRP_by_pruned,MRRP_by_quotient

cmdp_info = aev_examples.read_cmdp_data.cmdp_info("AEV_7378_cap200", 200)
mdp = cmdp_info.cmdp
cap = cmdp_info.cap
targets = cmdp_info.targets
SF = cmdp_info.SF
SFR = cmdp_info.SFR
SFRR = cmdp_info.SFRR



pruned_mdp, sstorm_result, p_strategy = MRRP_by_pruned(mdp, targets, cap, SF, SFR, SFRR)

quotient_mdp, ssstorm_result, q_strategy = MRRP_by_quotient(pruned_mdp, SFR, SFRR)


for i in pruned_mdp.states:
    ini_state = i[0]
    resource_level = i[1]
    print(f"-----MRP for state: ({ini_state},{resource_level})-----")


    ind = pruned_mdp.states.index((ini_state, resource_level))
    print("probability by pruned construction:", sstorm_result.at(ind))


    num = quotient_mdp.equivalence_class_map[(ini_state, resource_level)]
    ind = quotient_mdp.states.index(num)
    print("probability by quotient construction:", ssstorm_result.at(ind))




