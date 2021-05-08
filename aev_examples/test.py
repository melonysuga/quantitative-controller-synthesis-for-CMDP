from MRRP import cmdp2p_mdp_RR,p_mdp2q_mdp_RR,cmdp2n_mdp
import stormpy
from MRRP.mdp2stormpy import consmdp_to_storm_consmdp
from CMDP import strategy_extraction
import time

import aev_examples.read_cmdp_data

from MRRP.MRRP_calculate import MRRP_by_pruned,MRRP_by_quotient

cmdp_info = aev_examples.read_cmdp_data.cmdp_info("AEV_601_cap80", 80)
mdp = cmdp_info.cmdp
cap = cmdp_info.cap
targets = cmdp_info.targets
SF = cmdp_info.SF
SFR = cmdp_info.SFR
SFRR = cmdp_info.SFRR

formula = 'Pmax=? [F "target" ]'
prop = stormpy.parse_properties(formula)
def MRRP_by_pruned(mdp, targets, cap, SF):
    pruned_mdp = cmdp2n_mdp.naive_flattened_mdp(mdp, targets, cap, SF)
    print("mdp convert to pruned one successfully")

    pruned_storm_mdp = consmdp_to_storm_consmdp(pruned_mdp, pruned_mdp.new_targets)
    print(f"pruned------The number of states in the explicit MDP in Storm: {pruned_storm_mdp.nr_states}")
    print(f"transitions number:{pruned_storm_mdp.nr_transitions}")

    storm_result = stormpy.model_checking(pruned_storm_mdp, prop[0])
    for i in pruned_mdp.states:
        ini_state = i[0]
        resource_level = i[1]
        print(f"-----MRRP for state: ({ini_state},{resource_level})-----")

        ind = pruned_mdp.states.index((ini_state, resource_level))
        print("probability by pruned construction:", storm_result.at(ind))

    # t5 = time.time()
    strategy_extract = strategy_extraction.StrategyExtract(pruned_mdp, storm_result)
    strategy_result = strategy_extract.prob_vector
    # t6 = time.time()
    # print("runtime(s) of extracting optimal policy:", t6 - t5)
    return pruned_mdp,storm_result,strategy_result
MRRP_by_pruned(mdp, targets, cap, SF)

