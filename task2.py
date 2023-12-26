from random import randint, seed, uniform
import time
import datetime
from asyncio import sleep as sl
from spade import run, wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from math import fabs, sqrt
import pandas as pd

XMPP_server = "localhost"
Agent_prefix = "agent"

class MyAgent(Agent):
    def __init__(self, neighbours=[], value: int = 0, start_time: datetime=datetime.datetime.now(), *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.neighs = neighbours
        self.state = value
        self.alpha = 0.1
        self.messages = []
        self.control = 0
        self.curr = 0
        self.start_time = start_time

    class sender(PeriodicBehaviour):
        async def run(self):
            for n in self.agent.neighs:
                msg = Message(to=n)
                if (uniform(0, 1) > 0.15):
                    msg.body = str(self.agent.state + uniform(-5, 5))
                else:
                    msg.body = None
                msg.thread = str(self.counter)
                await sl(uniform(0,0.25))
                await self.send(msg)
            if self.counter == limit:
                self.kill()
            self.counter += 1
        async def on_end(self):
            # stop agent from behaviour
            await self.agent.stop()

        async def on_start(self):
            self.counter = 0
    class receiver(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                self.agent.curr += 1
                if msg.body is not None:
                    self.agent.messages.append(float(msg.body) - self.agent.state)
            if self.agent.curr == len(self.agent.neighs):
                for i in self.agent.messages:
                    self.agent.control += i
                self.agent.state += self.agent.alpha*self.agent.control
                self.agent.control = 0
                self.agent.messages = []
                self.agent.curr = 0


    async def setup(self):
        time.sleep(5)
        b = self.receiver()
        self.add_behaviour(b)

        self.add_behaviour(self.sender(period = 1, start_at = self.start_time))


graph = [
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [1, 7, 15]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [0, 2, 8]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [1, 3]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [2, 4]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [3, 5, 13]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [4, 6, 10]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [5, 7, 14]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [0, 6, 8]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [1, 7, 9, 12]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [8, 10]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [5, 9, 11]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [10, 12, 15]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [8, 11, 13]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [4, 12, 14]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [6, 13, 15]],
        [f"{Agent_prefix}{i}@{XMPP_server}" for i in [0, 14, 11]],
]


limit = 200

async def main():
    s = 0
    seed(10)
    agents = []
    values =[]
    start_at = datetime.datetime.now() + datetime.timedelta(seconds=60)
    for i in range(len(graph)):
        value = randint(0,100)
        values.append(value)
        s += value
        agent = MyAgent(graph[i], value, start_at, f"{Agent_prefix}{i}@{XMPP_server}", "mypass", verify_security = False)
        await agent.start(auto_register=False)
        agents.append(agent)
    print(f'Average sum = {s/len(graph)}')
    await wait_until_finished(agents[-1])
    data = {
        "agent": [str(i.name).split("@")[0] for i in agents],
        "initial state": [value for value in values],
        "state": [i.state for i in agents],
        "err": [fabs(i.state - s / len(graph)) for i in agents]
    }
    print(pd.DataFrame(data=data))

    print(f'Default var = {sqrt(sum([(i - s / len(graph)) ** 2 for i in values]) / len(graph))}')
    print(f"Variance = {sqrt(sum([(i.state - s / len(graph)) ** 2 for i in agents]) / len(graph))}")


if __name__ == '__main__':
    run(main())
    print('Done')