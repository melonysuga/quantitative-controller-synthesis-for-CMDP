import os
import sys
current_directory = os.path.dirname(os.path.abspath("test_gw.py"))
root_path = os.path.abspath(os.path.dirname(current_directory) + os.path.sep + ".")
sys.path.append(root_path)

from fimdp.io import prism_to_consmdp
from fimdp.energy_solvers import BasicES
from fimdp.objectives import BUCHI, SAFE, POS_REACH
import stormpy
from MRP.MRP_calculate import MRP_by_naive,MRP_by_pruned,MRP_by_quotient


constants = {
    "size_x" : 60,
    "size_y" : "size_x",
    "capacity" : 60,
}
mdp = prism_to_consmdp("gw_param.prism", constants=constants)
targets = [2789,2768,2915,2786,2566,2302,3408,2260,2641,2176,
           2695,2881,2893,3414,2361,1835,2199,2267,2967,2983,
           2672,2977,2176,2367,3326,3448,2903,2549,2659,3408,
           2776,2385,3185,3421,2195,3292,2109,2379,3018,3224,
           2559,3112,2956,2448,2294,2790,2464,3291,2294,2546,
           2200,625,676,729,2547,2386,2696,2177,2660,2295,2110]
for target in [2110]:
    print("========construction on randomly chosen target========")
    cap = 60
    targets = [target]
    solver = BasicES(mdp, cap, targets)

    SF = solver.get_min_levels(SAFE)
    SFR = solver.get_min_levels(POS_REACH)
    SFRR = solver.get_min_levels(BUCHI)

    formula = 'Pmax=? [F "target" ]'
    prop = stormpy.parse_properties(formula)

    bisimulation_mdp, nstorm_result, n_strategy = MRP_by_naive(mdp, targets, cap, SF)

    smart_mdp, storm_result, p_strategy = MRP_by_pruned(mdp, targets, cap, SF, SFR, SFRR)

    smarter_mdp, smarter_storm_result, q_strategy = MRP_by_quotient(smart_mdp, SFR, SFRR)

    # print("-----the MRP vector: get each entry when given an initial state and an initial resource level-----")
    # for state in smart_mdp.states:
    #     print(f"MRP for state: {state}")
    #     n_ind = bisimulation_mdp.states.index(state)
    #     print("by naive construction:",nstorm_result.at(n_ind))
    #     s_ind = smart_mdp.states.index(state)
    #     print("by pruned construction:",storm_result.at(s_ind))
    #     equivalence_class = smarter_mdp.equivalence_class_map[state]
    #     ind = smarter_mdp.states.index(equivalence_class)
    #     print("by quotient construction:",smarter_storm_result.at(ind))

