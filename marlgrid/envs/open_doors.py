import numpy as np

from marlgrid.base import MultiGrid, MultiGridEnv
from marlgrid.objects import Door


class OpenDoorsMultiGrid(MultiGridEnv):
    COLORS = ["red", "blue", "purple", "orange", "olive", "pink"]

    def _gen_grid(self, width, height):
        self.grid = MultiGrid((width, height))
        self.grid.wall_rect(0, 0, width, height)
        self.doors = []

        wall_idxs = [
            list(range(1, width - 1)),
            list(range(1, width - 1)),
            list(range(1, height - 1)),
            list(range(1, height - 1)),
        ]

        for i in range(len(self.agents)):
            pos = [0, 0]
            side_idx = self.np_random.randint(0, len(wall_idxs))
            idx = self.np_random.randint(0, len(wall_idxs[side_idx]))
            pos[side_idx // 2] = wall_idxs[side_idx][idx]
            wall_idxs[side_idx].pop(idx)

            if side_idx == 0 or side_idx == 1:
                pos[1] = side_idx * (height - 1)
            else:
                pos[0] = (side_idx - 2) * (width - 1)

            door = AgentDoor(color=self.COLORS[i], state=Door.states.closed)
            self.doors.append(door)
            self.put_obj(door, pos[0], pos[1])

        self.place_agents()
        
    def reset(self, **kwargs):
        obs = super().reset(**kwargs)
        return np.stack(obs)
    
    def step(self, actions):
        obs, step_rewards, done, info = super().step(actions)
        done = False
        step_rewards = np.zeros(self.num_agents, dtype=float)
        doors_state = [door.state == Door.states.open for door in self.doors]

        if self._doors_opened_by_order(doors_state) is False:
            done = True
        elif all(doors_state):
            done = True
            step_rewards += 1

        return np.stack(obs), step_rewards, done, info

    def _doors_opened_by_order(self, doors):
        seen_closed_door = False

        for door in doors:
            if door is False:
                seen_closed_door = True
            elif door is True and seen_closed_door is True:
                return False

        return True

class SimpleDoor(Door):
    def __init__(self, color="worst", state=0):
        super().__init__(color, state)

        if self.state == Door.states.locked:
            self.state = Door.states.closed

    def can_overlap(self):
        return False
