import fimdp

'''
-------------------------------------------------
convert mdp to smart_mdp by absorbing some states
thus, the state space is much smaller than before
-------------------------------------------------
'''

class naive_flattened_mdp:
    def __init__(self, cmdp, targets, capacity, SF):
        self.cmdp = cmdp
        self.targets = targets
        self.capacity = capacity
        self.SF = SF

        self.new_targets = []

        self.reload = []

        self.states = []
        self.num_states = 0
        self.mdp_state_generate()

        #self.sink_id = self.num_states
        #self.num_states += 1

        self.succ = [0] * self.num_states


        self.actions = [0]
        self.mdp_actions_generate()

    def max_SF(self, ele):
        sfmax_value = set()
        for key in ele.distr.keys():
            sfmax_value.add(self.SF[key])
        return max(sfmax_value)

    def is_reload(self, s):
        return self.reload[s]

    def mdp_state_generate(self):
        for i in range(self.cmdp.num_states):
            j = self.capacity
            while j >= 0:
                if j >= self.SF[i]:
                    s_l = (i, j)
                    self.states.append(s_l)
                    if i in self.targets and j >= self.SF[i]:
                    # if i in self.targets:
                        self.new_targets.append(self.num_states)
                    if self.cmdp.is_reload(i):
                        self.reload.append(True)
                    else:
                        self.reload.append(False)
                    self.num_states += 1
                j = j - 1

    def add_action(self, src, distribution, label, consumption):
        if src >= self.num_states:
            raise ValueError(f"State {src} exceeds the index of states")

        for k in distribution.keys():
            if k >= self.num_states:
                raise  ValueError(f"State {k} exceeds the index of states")

        for a in self.actions_for_state(src):
            if label == a.label:
                raise ValueError("State {} already has an action with label {}".format(src,label))

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

    def mdp_actions_generate(self):
        sink_created = False
        for i in range(self.num_states):
            s, resource_level = self.states[i][0], self.states[i][1]
            for ele in self.cmdp.actions_for_state(s):
                cons = ele.cons
                label = ele.label
                if resource_level >= cons + self.max_SF(ele):
                    distr = {}
                    for key in ele.distr.keys():
                        if self.cmdp.is_reload(key):
                            succ = (key, self.capacity)
                        else:
                            succ = (key, resource_level - cons)
                        succ_index = self.states.index(succ)
                        prob = ele.distr[key]
                        distr[succ_index] = prob
                    self.add_action(i, distr, label, cons)
                else:
                    # if not sink_created:
                    #    self.states.append((-1, -1))
                    #    self.reload.append(False)
                    #    self.add_action(self.sink_id, {self.sink_id: 1}, "σ", 0)
                    #    sink_created = True
                    self.add_action(i, {i: 1}, label, 0)



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

