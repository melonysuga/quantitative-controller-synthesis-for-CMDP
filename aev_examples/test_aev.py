import aev_examples.read_cmdp_data
import time
from MRP.MRP_calculate import MRP_by_naive,MRP_by_pruned,MRP_by_quotient

cmdp_info = aev_examples.read_cmdp_data.cmdp_info("AEV_601_cap80", 80)
mdp = cmdp_info.cmdp
for state in range(mdp.num_states):
    print("-----------------------")
    for action in mdp.actions_for_state(state):
        print(action.label)