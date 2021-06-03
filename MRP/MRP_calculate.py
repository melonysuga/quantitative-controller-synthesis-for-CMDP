from MRP import cmdp2n_mdp,cmdp2p_mdp,p_mdp2q_mdp
import stormpy
from MRP.mdp2stormpy import consmdp_to_storm_consmdp
import time
from CMDP import strategy_extraction
import psutil
import os
import sys


formula = 'Pmax=? [F "target" ]'
prop = stormpy.parse_properties(formula)

def MRP_by_naive(mdp, targets, cap, SF):

    t1 = time.time()
    naive_flattened_mdp = cmdp2n_mdp.naive_flattened_mdp(mdp, targets, cap, SF)


    print("cmdp convert to mdp successfully")


    storm_mdp = consmdp_to_storm_consmdp(naive_flattened_mdp, naive_flattened_mdp.new_targets)
    print(f"naive-------The number of states in the explicit MDP in Storm: {storm_mdp.nr_states}")
    print(f"transitions number:{storm_mdp.nr_transitions}")

    nstorm_result = stormpy.model_checking(storm_mdp, prop[0])

    strategy_extract = strategy_extraction.StrategyExtract(naive_flattened_mdp, nstorm_result)
    strategy_result = strategy_extract.extractOptAction()
    t2 = time.time()


    print("runtime(s) of computing MRP by naive flattened mdp and extracting optimal policy:", t2 - t1)
    return naive_flattened_mdp, nstorm_result, strategy_result


def MRP_by_pruned(mdp, targets, cap, SF, SFR, SFRR):

    t1 = time.time()
    pruned_mdp = cmdp2p_mdp.pruned_mdp(mdp, targets, cap, SF, SFR, SFRR)
    # pruned_mdp = cmdp2smdp_RR.pruned_mdp(mdp, targets, cap, SF, SFR, SFRR)

    print("mdp convert to pruned one successfully")

    pruned_storm_mdp = consmdp_to_storm_consmdp(pruned_mdp, pruned_mdp.new_targets)
    print(f"pruned------The number of states in the explicit MDP in Storm: {pruned_storm_mdp.nr_states}")
    print(f"transitions number:{pruned_storm_mdp.nr_transitions}")

    storm_result = stormpy.model_checking(pruned_storm_mdp, prop[0])

    strategy_extract = strategy_extraction.StrategyExtract(pruned_mdp, storm_result)
    strategy_result = strategy_extract.extractOptAction()
    t2 = time.time()
    print("runtime(s) of computing MRP by prunning flattened mdp and extracting optimal policy:" , t2 - t1)

    return pruned_mdp,storm_result, strategy_result


def MRP_by_quotient(pruned_mdp, SFR, SFRR):

    t1 = time.time()
    quotient_mdp = p_mdp2q_mdp.quotient_mdp(pruned_mdp, SFR, SFRR)

    print("pruned convert to quotient successfully")


    quotient_storm_mdp = consmdp_to_storm_consmdp(quotient_mdp, quotient_mdp.new_targets)
    print(f"quotient-----The number of states in the explicit MDP in Storm: {quotient_storm_mdp.nr_states}")
    print(f"transitions number:{quotient_storm_mdp.nr_transitions}")

    quotient_storm_result = stormpy.model_checking(quotient_storm_mdp, prop[0])


    strategy_extract = strategy_extraction.StrategyExtract(quotient_mdp, quotient_storm_result)
    strategy_result = strategy_extract.extractOptAction()
    t2 = time.time()
    print("runtime(s) of computing MRP by quotient flattened mdp and extracting optimal policy:", t2 - t1)

    return quotient_mdp, quotient_storm_result, strategy_result


