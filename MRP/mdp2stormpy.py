import stormpy


def consmdp_to_storm_consmdp(cons_mdp, targets=None):
    """
    Convert a ConsMDP object from FiMDP into a Storm's SparseMDP representation.

    The conversion works in reversible way. In particular, it does not encode
    the energy levels into state-space. Instead, it uses the encoding using
    rewards.

    The reloading and target states (if given) are encoded using state-labels
    in the similar fashion.

    :param cons_mdp: ConsMDP object to be converted
    :param targets: A list of targets (default None). If specified, each state
    in this list is labeled with the label `target`.
    :return: SparseMDP representation from Stormpy of the cons_mdp.
    """
    builder = stormpy.SparseMatrixBuilder(rows=0, columns=0, entries=0,
                                          force_dimensions=False,
                                          has_custom_row_grouping=True,
                                          row_groups=0)
    action_c = 0
    consumption = []
    action_labeling = stormpy.storage.ChoiceLabeling(len(cons_mdp.actions))

    for state in range(cons_mdp.num_states):
        # Each state has its own group
        # Each row is one action (choice)
        builder.new_row_group(action_c)

        for action in cons_mdp.actions_for_state(state):
            for dst, prob in action.distr.items():
                builder.add_next_value(action_c, dst, prob)

            consumption.append(action.cons)

            if action.label not in action_labeling.get_labels():
                action_labeling.add_label(action.label)
            action_labeling.add_label_to_choice(action.label, action_c)

            action_c += 1
    builder.add_next_value(action_c, cons_mdp.num_states-1, 0)
    consumption.append(0)
    action_labeling.add_label("auxilary_edge")
    action_labeling.add_label_to_choice("auxilary_edge", action_c)

    transitions = builder.build()

    # Consumption
    cons_rew = stormpy.SparseRewardModel(
        optional_state_action_reward_vector=consumption)
    rewards = {"consumption": cons_rew}

    # Reloads
    state_labeling = stormpy.storage.StateLabeling(cons_mdp.num_states)


    # Targets
    if targets is not None:
        state_labeling.add_label("target")
        for state in targets:
            state_labeling.add_label_to_state("target", state)

    # Plug it all together
    components = stormpy.SparseModelComponents(
        transition_matrix=transitions,
        state_labeling=state_labeling,
        reward_models=rewards,
        rate_transitions=False)
    components.choice_labeling = action_labeling

    st_mdp = stormpy.storage.SparseMdp(components)

    return st_mdp