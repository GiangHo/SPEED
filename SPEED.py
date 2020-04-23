# -*- coding: utf-8 -*-


def opposite_event(event):
    if event.isupper():
        return event.lower()
    else:
        return event.upper()


def get_episode(event_flow, event):
    episode = None
    for i in range(len(event_flow) - 1):
        if event_flow[i] == event:
            episode = event_flow[i:]
            break
    return episode


def get_all_context(event_flow):
    return ['_'.join(map(str, event_flow[i:j + 1])) for i in range(len(event_flow)) for j in range(i, len(event_flow))]


def update_tree_value(contexts):
    tree_value = {}
    for i in contexts:
        if tree_value.get(i) is None:
            tree_value[i] = 1
        else:
            tree_value[i] += 1
    return tree_value


def gen_episode(actions):
    event_flow = []
    max_episode_length = 1
    contexts = []

    for i in actions.split("_"):
        event_flow.append(i)
        episode = get_episode(event_flow, opposite_event(str(i)))
        if episode is not None:
            if len(episode) > max_episode_length:
                max_episode_length = len(episode)
            event_flow = event_flow[(len(event_flow) - max_episode_length):]
            contexts += get_all_context(episode)
    return contexts


def gen_tree(actions):
    tree_node = {}
    tree_roots = []

    contexts = gen_episode(actions)
    unique_contexts = set(contexts)

    tree_value = update_tree_value(contexts)
    print("______________Tree value_______________")
    for k, v in sorted(tree_value.items()):
        print(str(k) + ": " + str(v))

    for context in unique_contexts:
        if "_" not in context:
            tree_roots.append(context)
        else:
            context_tmp = context.rsplit("_", 1)
            if tree_node.get(context_tmp[0]) is None:
                value = set()
                value.add(context_tmp[1])
                tree_node[context_tmp[0]] = value
            else:
                value = tree_node[context_tmp[0]]
                value.add(context_tmp[1])
                tree_node[context_tmp[0]] = value

    print("______________Tree roots_______________")
    print(tree_roots)

    print("______________Tree node_______________")
    for k, v in tree_node.items():
        print(str(k) + ": " + str(v))

    return tree_roots, tree_node, tree_value


def get_escape_cost(node, tree_node, tree_value):
    children_node = tree_node.get(node)
    escape_cost = 0

    if children_node is not None:
        chidren_cost = 0
        for child_node in children_node:
            chidren_cost += tree_value.get(node + "_" + child_node)
        escape_cost = tree_value.get(node) - chidren_cost
    return escape_cost


def predict_event(input_sequence, candidate, tree_roots, tree_node, tree_value):
    input_sequence_tmp = input_sequence.split("_")
    suffixes = ["_".join(map(str, input_sequence_tmp[0:i + 1])) for i in range(len(input_sequence_tmp))]

    print("___________Predict with candidate: " + candidate + "____________")
    print("suffixes", suffixes)

    total_cost = 0
    for i in tree_roots:
        total_cost += tree_value.get(i)
    candidate_prob = tree_value.get(candidate) / total_cost
    print("candidate_prob " + candidate + ": ", tree_value.get(candidate), "/", total_cost)

    for suffix in suffixes:
        print("term: " + suffix)
        escape_prob = 0
        term_prob = 0

        if tree_value.get(suffix) is not None:
            escape_cost = get_escape_cost(suffix, tree_node, tree_value)
            escape_prob = escape_cost / tree_value.get(suffix)
            print("escape_prob: ", escape_cost, "/", tree_value.get(suffix))

            term_cost = tree_value.get(suffix + "_" + candidate)
            if term_cost is None:
                term_cost = 0
            term_prob = term_cost / tree_value.get(suffix)

            print("term_prob: ", term_cost, "/", tree_value.get(suffix))
            print("P_partial = ", candidate_prob, "*", escape_prob, "+", term_prob)

        candidate_prob = candidate_prob * escape_prob + term_prob

    print("P = ", candidate_prob)
    return candidate_prob


if __name__ == '__main__':
    actions = "A_B_b_D_C_c_a_B_C_b_d_c_A_D_a_B_A_d_a_b"
    tree_roots, tree_node, tree_value = gen_tree(actions)

    max_prob = 0
    next_event = ""
    for candidate in tree_roots:
        candidate_prob = predict_event("A_d_a", candidate, tree_roots, tree_node, tree_value)
        if candidate_prob > max_prob:
            max_prob = candidate_prob
            next_event = candidate
    print("______________Result_______________")
    print("max_prob", max_prob)
    print("next_event", next_event)
