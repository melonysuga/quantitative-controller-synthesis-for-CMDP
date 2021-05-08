import fimdp
import math
import copy
import os,psutil

'''
-------------------------------------------------
convert mdp to smart_mdp by absorbing some states
thus, the state space is much smaller than before
-------------------------------------------------
'''


class pruned_mdp:
    def __init__(self, cmdp, targets, capacity, SF, SFR, SFRR):
        self.cmdp = cmdp
        self.targets = targets
        self.capacity = capacity
        self.SF = SF
        self.SFR = SFR
        self.SFRR = SFRR

        self.new_targets = []
        self.states = []
        self.num_states = 0

        self.visit = {}

        self.succ = []
        self.actions = [0]
        mem1 = psutil.Process(os.getpid()).memory_info().rss

        self.all_mdp_generate()

        mem2 = psutil.Process(os.getpid()).memory_info().rss

        self.sink_id = self.num_states
        self.num_states += 1
        self.succ.append(0)
        self.add_action(self.sink_id, {self.sink_id: 1}, "sink", 0)
        self.memory = (mem2 - mem1) / 1024


    def all_mdp_generate(self):
        S = set()
        # visit = {}
        for i in range(self.cmdp.num_states):
            if i not in self.targets:
                j = self.capacity
                while j >= 0:
                    if self.SFR[i] <= j < self.SFRR[i]:
                    #if j >= self.SF[i]:
                        s_l = (i, j)
                        S.add(s_l)
                        # visit[s_l] = False
                    j -= 1
        while len(S) > 0:
            for (i, j) in S:
                # if not visit[(i, j)]:
                self.mdp_generate(i, j)
                # visit[(i, j)] = True
                if len(S & set(self.states)) != 0:
                    S = S - set(self.states)
                break

    def is_reload(self, s):
        return self.reload[s]

    def mdp_generate(self, ini_state, resource_level):
        self.states.append((ini_state, resource_level))
        self.num_states += 1
        self.succ.append(0)
        self.visit[(ini_state, resource_level)] = False
        component = {(ini_state, resource_level)}
        while True:
            comp = copy.deepcopy(component)
            for i in comp:
                if not self.visit[i]:
                    self.visit[i] = True
                    if (i[0] in self.targets and i[1] >= self.SF[i[0]]) or i[1] >= self.SFRR[i[0]]:
                        self.new_targets.append(self.states.index(i))
                        self.add_action(self.states.index(i), {self.states.index(i): 1}, "self_absorbed", 0)
                    elif i[1] < self.SFR[i[0]]:
                        self.add_action(self.states.index(i), {self.states.index(i): 1}, "self_absorbed", 0)
                    else:
                        have_action = False
                        for ele in self.cmdp.actions_for_state(i[0]):
                            cons = ele.cons
                            label = ele.label
                            l = i[1] - cons
                            if l >= max(self.max_SF(ele), self.min_SFR(ele)):
                                have_action = True
                                distr = {}
                                for key in ele.distr.keys():
                                    l = i[1] - cons
                                    s = key
                                    if self.cmdp.is_reload(key):
                                        l = self.capacity
                                    if (s, l) not in self.visit.keys():
                                        self.states.append((s, l))
                                        distr[self.num_states] = ele.distr[key]
                                        self.num_states += 1
                                        self.succ.append(0)
                                        component.add((s, l))
                                        self.visit[(s, l)] = False
                                    else:
                                        succ_index = self.states.index((s, l))
                                        distr[succ_index] = ele.distr[key]
                                self.add_action(self.states.index(i), distr, label, cons)
                        if not have_action:
                            self.add_action(self.states.index(i), {self.states.index(i): 1}, "self_absorbed", 0)
            if comp.issubset(component) and component.issubset(comp):
                break

    def add_action(self, src, distribution, label, consumption):
        if src >= self.num_states:
            raise ValueError(f"State {src} exceeds the index of states")

        for k in list(distribution.keys()):
            if k >= self.num_states:
                raise ValueError(f"State {k} exceeds the index of states")

        for a in self.actions_for_state(src):
            if label == a.label:
                raise ValueError("State {} already has an action with label {}".format(src, label))

        aid = len(self.actions)
        adata = ActionData(src, consumption, distribution, label, 0)

        a = self.actions_for_state(src).get_last()
        if a is None:
            self.succ[src] = aid
        else:
            a.next_succ = aid

        self.actions.append(adata)
        return aid

    def actions_for_state(self, s):
        it = Action_Succ_Iter(self.actions, self.succ[s])
        return it

    def max_SF(self, ele):
        max_value = 0
        for key in list(ele.distr.keys()):
            if not self.cmdp.is_reload(key):
                max_value = max(max_value, self.SF[key])
            elif self.cmdp.is_reload(key) and self.SF[key] == math.inf:
                max_value = math.inf
        return max_value

    def min_SFR(self, ele):
        min_value = math.inf
        for key in list(ele.distr.keys()):
            min_value = min(min_value, self.SFR[key])
        return min_value


class ActionData:
    def __init__(self, src, cons, distr, label, next_succ):
        self.src = src
        self.cons = cons
        self.distr = distr
        self.label = label
        self.next_succ = next_succ

    def get_succs(self):
        return set(self.distr.keys())


class Action_Succ_Iter():
    def __init__(self, actions, succ_index):
        self.actions = actions
        self.succ_next = succ_index

    def __iter__(self):
        return self

    def __next__(self):
        if self.succ_next == 0:
            raise StopIteration()
        if self.succ_next >= len(self.actions):
            raise IndexError("{}".format(self.actions) + f"{self.succ_next}")
        else:
            action = self.actions[self.succ_next]
            self.succ_next = action.next_succ
        return action

    def is_empty(self):
        return self.succ_next == 0

    def get_last(self):
        a = None
        while not self.is_empty():
            a = self.__next__()
        return a

