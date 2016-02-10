import pyflo.component

import numpy
import transitions
from collections import deque


class SplitComponent(pyflo.component.Component):
    axis = None

    def __init__(self, metadata):
        inports = {
            "in": {},
            "axis": {},
        }
        outports = {
            "out": {},
        }
        super().__init__(inports, outports)
        self.inports["in"].on("data", self.data)
        self.inports["axis"].on("data", self.set_axis)

    @pyflo.component.wait_for('axis')
    def data(self, data, axis):
        if axis is None:
            axis = 0
        else:
            axis = int(axis)
        self.outports["out"].begin_group()
        num_subarrays = data.shape[axis]
        for subarray in numpy.split(data, num_subarrays, axis=axis):
            self.outports["out"].send_data(subarray.squeeze())
        self.outports["out"].end_group()

    @pyflo.component.empty_queue
    def set_axis(self, axis):
        self.axis = int(axis)


class StackComponent(pyflo.component.Component):
    axis = None
    group_level = 0
    current_data = None

    def __init__(self, metadata):
        inports = {
            "in": {},
            "axis": {},
        }
        outports = {
            "out": {},
        }
        super().__init__(inports, outports)
        self.queued_data = deque()

        self.machine = transitions.Machine(model=self, states=['start', 'middle', 'end'], initial='end')
        self.machine.add_transition('begin_group', 'start', 'start', before='pass_begin')
        self.machine.add_transition('begin_group', 'end', 'start')
        self.machine.add_transition('data', 'start', 'middle', before='initialise_group')
        self.machine.add_transition('data', 'middle', 'middle')
        self.machine.add_transition('end_group', 'middle', 'end', after='process_data')
        self.machine.add_transition('end_group', 'end', 'end', before='pass_end')

        self.inports["in"].on("data", self.data)
        self.inports["in"].on("beginGroup", self.begin_group)
        self.inports["in"].on("endGroup", self.end_group)
        self.inports["axis"].on("data", self.set_axis)

    def pass_begin(self):
        if len(self.queued_data) == 0:
            self.outports["out"].begin_group()
        else:
            self.queued_data.append(self.outports["out"].begin_group)

    def pass_end(self):
        if len(self.queued_data) == 0:
            self.outports["out"].end_group()
        else:
            self.queued_data.append(self.outports["out"].end_group)

    def initialise_group(self, data):
        self.current_data = []

    def process_data(self):
        if self.get_axis() is None:
            self.queued_data.append(self.current_data)
            return
        self.stack_data(self.current_data, self.get_axis())

    def get_axis(self):
        if self.inports["axis"].attached():
            return self.axis
        return 0

    def stack_data(self, data, axis):
        stacked_data = numpy.stack(data, axis=axis)
        self.outports["out"].send_data(stacked_data)

    def set_axis(self, axis):
        self.axis = int(axis)
        while len(self.queued_data) > 0:
            action = self.queued_data.popleft()
            if isinstance(action, list):
                self.stack_data(action, self.axis)
            else:
                action()

    def on_enter_middle(self, data):
        self.current_data.append(data)
