# -*- coding: utf-8 -*-


def get_actions_by_day(file_path):
    event_flow = {}
    with open(file_path, "r") as fp:
        for line in fp:
            event = line.replace("\n", "").split(" ")

            if event[-1] == "OFF":
                off_event = str(event[-2]).lower()
                event[-2] = off_event
            if (event_flow.get(event[0])) is None:
                event_flow[event[0]] = str(event[-2])
            else:
                event_flow[event[0]] += "_" + str(event[-2])
    print("__________Actions by day__________")
    for k, v in event_flow.items():
        print(k, ": ", v)

if __name__ == '__main__':
    get_actions_by_day("march.in.new")
