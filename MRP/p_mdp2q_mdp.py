import math
import copy
import os,psutil



class quotient_mdp():
    def __init__(self, s_mdp, SFR, SFRR):
        self.s_mdp = s_mdp
        self.SFR = SFR
        self.SFRR = SFRR

        self.states = []

        self.actions = [0]
        self.succ = []

        self.num_states = 0

        self.new_targets = []

        self.equivalence_class_map = {}
        mem1 = psutil.Process(os.getpid()).memory_info().rss
        self.construct_quotient_mdp()
        self.reload = [False] * self.num_states
        mem2 = psutil.Process(os.getpid()).memory_info().rss
        self.memory = (mem2 - mem1) / 1024

    def is_reload(self, s):
        return self.reload[s]

    def construct_quotient_mdp(self):
        for state in self.s_mdp.states:
            s, l = state[0], state[1]
            if s in self.s_mdp.targets or l >= self.SFRR[s]:
                self.equivalence_class_map[state] = "top"
            elif l < self.SFR[s]:
                self.equivalence_class_map[state] = "bot"
            else:
                ini_equivalence_class = self.ini_equivalence_class(s)
                self.equivalence_class_map[state] = (s, ini_equivalence_class)

                if (s, ini_equivalence_class) not in self.states:
                    self.states.append((s, ini_equivalence_class))
                    self.succ.append(0)
                    self.num_states += 1

        while True:
            state_prime = copy.deepcopy(self.states)

            for state in state_prime:
                s, l, u = state[0], state[1][0], state[1][1]
                if l != u:
                    split, l_prime, u_prime = self.split_equivalence_class(s, (l, u))

                    if split:

                        self.succ.pop(self.states.index(state))
                        self.states.remove(state)
                        self.num_states -= 1

                        self.states.append((s, (l, u_prime)))
                        self.succ.append(0)
                        self.num_states += 1

                        self.states.append((s, (l_prime, u)))
                        self.succ.append(0)
                        self.num_states += 1

                        for ll in range(l, u + 1):
                            if (s,ll) in self.s_mdp.states and l <= ll <= u_prime:
                                self.equivalence_class_map[(s, ll)] = (s, (l, u_prime))
                            elif (s,ll) in self.s_mdp.states:
                                self.equivalence_class_map[(s, ll)] = (s, (l_prime, u))
                        break
                    else:
                        been_second_split = False
                        for action in self.s_mdp.actions_for_state(self.s_mdp.states.index((s, l))):
                            for key in action.distr.keys():
                                t, k = self.s_mdp.states[key]
                                split, l_prime, u_prime = self.split_equivalence_class_2(s, l, u, t, k)

                                if split:

                                    been_second_split = True

                                    self.succ.pop(self.states.index(state))
                                    self.states.remove(state)
                                    self.num_states -= 1

                                    self.states.append((s, (l, u_prime)))
                                    self.succ.append(0)
                                    self.num_states += 1

                                    self.states.append((s, (l_prime, u)))
                                    self.succ.append(0)
                                    self.num_states += 1

                                    for ll in range(l, u + 1):
                                        if (s, ll) in self.s_mdp.states and l <= ll <= u_prime:
                                            self.equivalence_class_map[(s, ll)] = (s, (l, u_prime))
                                        elif (s, ll) in self.s_mdp.states:
                                            self.equivalence_class_map[(s, ll)] = (s, (l_prime, u))
                                    break
                            if been_second_split:
                                break
                        if been_second_split:
                            break
            # do not stop until no split
            if state_prime == self.states:
                break

        # at least one outgoing transition for each state
        self.states.append("top")
        self.succ.append(0)
        self.num_states += 1
        self.states.append("bot")
        self.succ.append(0)
        self.num_states += 1
        self.add_action(self.num_states-2, {self.num_states-2: 1}, "top_absorbed", 0)
        self.add_action(self.num_states-1, {self.num_states-1: 1}, "bot_absorbed", 0)
        self.new_targets.append(self.num_states-2)
        # self.states.append("sink")
        # self.succ.append(0)
        # self.num_states += 1
        # self.add_action(self.num_states-1, {self.num_states-1: 1}, "sink_repeated", 0)

        for state in self.states:
            if state != "top" and state != "bot":
                s, inf = state[0], state[1][0]
                src_index = self.states.index(state)

                #print the information of successors of both (s,inf) and (s, sup)
                # print(f"inf---the information of successors for {state}")
                # for action in self.s_mdp.actions_for_state(self.s_mdp.states.index((s, inf))):
                #     print("label:", action.label)
                #     print("distribution:")
                #     for key in action.distr.keys():
                #         succ = self.equivalence_class_map[self.s_mdp.states[key]]
                #         prop = action.distr[key]
                #         print(f"successor equivalence class:{succ}, ini_state_resource:{self.s_mdp.states[key]},probability:{prop}")
                #
                # print(f"sup---the information of successors for {state}")
                # print the information of successors of both (s,inf) and (s, sup)
                # for action in self.s_mdp.actions_for_state(self.s_mdp.states.index((s, sup))):
                #     print("label:", action.label)
                #     print("distribution:")
                #     for key in action.distr.keys():
                #         succ = self.equivalence_class_map[self.s_mdp.states[key]]
                #         prop = action.distr[key]
                #         print(f"successor equivalence class:{succ},ini_state_resource:{self.s_mdp.states[key]}, probability:{prop}")

                for action in self.s_mdp.actions_for_state(self.s_mdp.states.index((s, inf))):
                    label = action.label
                    cons = action.cons
                    distr = {}
                    for key in action.distr.keys():
                        succ_index = self.states.index(self.equivalence_class_map[self.s_mdp.states[key]])
                        if succ_index in distr.keys():
                            distr[succ_index] += action.distr[key]
                        else:
                            distr[succ_index] = action.distr[key]
                    self.add_action(src_index, distr, label, cons)

    def split_equivalence_class_2(self, s, l, u, t, k):
        split = False
        l_prime = None
        u_prime = None
        for ll in range(l, u + 1):
            if not self.s_mdp.cmdp.is_reload(t) and (s, ll) in self.s_mdp.states:
                if self.equivalence_class_map[(t,k)] != self.equivalence_class_map[(t, k + ll - l)]:
                    split = True
                    l_prime = ll
                    break
                else:
                    u_prime = ll
        return split, l_prime, u_prime

    def split_equivalence_class(self, state, class_range):
        split, l_prime, u_prime = False, None, None
        action_l = set()
        for action in self.s_mdp.actions_for_state(self.s_mdp.states.index((state, class_range[0]))):
            action_l.add(action.label)
        for ll in range(class_range[0], class_range[1] + 1):
            if (state, ll) in self.s_mdp.states:
                action_ll = set()
                for action in self.s_mdp.actions_for_state(self.s_mdp.states.index((state, ll))):
                    action_ll.add(action.label)
                if not action_l.issubset(action_ll) or not action_ll.issubset(action_l):
                    split = True
                    l_prime = ll
                    break
                else:
                    u_prime = ll
        return split, l_prime, u_prime

    def ini_equivalence_class(self, equivalence_state):
        min_value = math.inf
        max_value = 0
        for state in self.s_mdp.states:
            s, l = state[0], state[1]
            if s == equivalence_state:
                if self.SFR[s] <= l < self.SFRR[s]:
                    min_value = min(min_value, l)
                    max_value = max(max_value, l)
        return min_value, max_value

    def add_action(self, src, distribution, label, cons):
        if src >= self.num_states:
            raise ValueError(f"State {src} exceeds the index of states")

        for k in distribution.keys():
            if k >= self.num_states:
                raise ValueError(f"State {k} exceeds the index of states")

        for a in self.actions_for_state(src):
            if label == a.label:
                raise ValueError("State {} already has an action with label {}".format(src,label))

        aid = len(self.actions)
        adata = ActionData(src, cons, distribution, label, 0)

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
        if self.succ_next>= len(self.actions):
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