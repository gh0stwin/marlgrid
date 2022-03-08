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

    def step(self, actions):
        obs, step_rewards, done, info = super().step(actions)
        opened_doors = map(lambda door: door.state == Door.states.open, self.doors)

        if any(opened_doors):
            done = True

        if all(opened_doors):
            step_rewards = [1 for _ in range(self.num_agents)]
        else:
            step_rewards = [0 for _ in range(self.num_agents)]

        return obs, step_rewards, done, info


class AgentDoor(Door):
    def __init__(self, color="worst", state=0):
        super().__init__(color, state)

        if self.state == Door.states.locked:
            self.state = Door.states.closed

    def toggle(self, agent, pos):
        if self.state == Door.states.closed and self.color == agent.color:
            self.state = Door.states.open
        elif self.state == self.states.open and self.color == agent.color:
            self.state = self.states.closed

        return True
