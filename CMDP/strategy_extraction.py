"""
After getting maximal (repeated) reachability probability by model checker STORMPY,
we get a maximal (repeated) reachability probability vector in the state space.
Substitute the optimal vector into the Bellman Equation backup operator,
we can get the optimal action selected according to the given state.
"""
from decimal import Decimal

class StrategyExtract:

    def __init__(self, mdp_model, prob_vector):
        self.mdp = mdp_model
        self.prob_vector = prob_vector

    def extractOptAction(self):
        state_policy_map = {}
        for i in self.mdp.states:
            state = (i[0], i[1])
            ind = self.mdp.states.index(state)
            if ind in self.mdp.new_targets:
                state_policy_map[ind] = ('#', self.prob_vector.at(ind))
            else:
                max_pro = 0
                action_label = ""
                for action in self.mdp.actions_for_state(ind):
                    cons = action.cons
                    label = action.label
                    prob = 0
                    for key in action.distr.keys():
                        if key in self.prob_vector.new_targets:
                            prob += action.distr[key]
                        else:
                            prob += (action.distr[key] * Decimal.from_float(self.prob_vector.at(key)))
                    if prob > max_pro:
                        max_pro = prob
                        action_label = label
                state_policy_map[ind] = (action_label, max_pro)
        return state_policy_map
