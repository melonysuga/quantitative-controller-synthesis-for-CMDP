from MRRP import cmdp2p_mdp_RR,p_mdp2q_mdp_RR
import stormpy
from MRRP.mdp2stormpy import consmdp_to_storm_consmdp
from CMDP import strategy_extraction
import time
import os
import psutil


formula = 'Pmax=? [F "target" ]'
prop = stormpy.parse_properties(formula)




def MRRP_by_pruned(mdp, targets, cap, SF, SFR, SFRR):
    t1 = time.time()
    pruned_mdp = cmdp2p_mdp_RR.pruned_mdp(mdp, targets, cap, SF, SFR, SFRR)
    print("mdp convert to pruned one successfully")

    pruned_storm_mdp = consmdp_to_storm_consmdp(pruned_mdp, pruned_mdp.new_targets)
    print(f"pruned------The number of states in the explicit MDP in Storm: {pruned_storm_mdp.nr_states}")
    print(f"transitions number:{pruned_storm_mdp.nr_transitions}")

    storm_result = stormpy.model_checking(pruned_storm_mdp, prop[0])


    strategy_extract = strategy_extraction.StrategyExtract(pruned_mdp, storm_result)
    strategy_result = strategy_extract.extractOptAction()
    t2 = time.time()
    print("runtime(s) of computing MRRP by prunning flattened mdp and extracting optimal policy:", t2 - t1)
    return pruned_mdp,storm_result,strategy_result


def MRRP_by_quotient(pruned_mdp, SFR, SFRR):
    t1 = time.time()
    quotient_mdp = p_mdp2q_mdp_RR.quotient_mdp(pruned_mdp, SFR, SFRR)
    print("pruned convert to quotient successfully")

    quotient_storm_mdp = consmdp_to_storm_consmdp(quotient_mdp, quotient_mdp.new_targets)
    print(f"quotient-----The number of states in the explicit MDP in Storm: {quotient_storm_mdp.nr_states}")
    print(f"transitions number:{quotient_storm_mdp.nr_transitions}")

    quotient_storm_result = stormpy.model_checking(quotient_storm_mdp, prop[0])

    # t5 = time.time()
    strategy_extract = strategy_extraction.StrategyExtract(quotient_mdp, quotient_storm_result)
    strategy_result = strategy_extract.extractOptAction()
    # t6 = time.time()
    # print("runtime(s) of extracting optimal policy:", t6 - t5)
    t2 = time.time()
    print("runtime(s) of computing MRRP by quotient flattened mdp and extracting optimal policy:", t2 - t1)
    return quotient_mdp, quotient_storm_result, strategy_result
