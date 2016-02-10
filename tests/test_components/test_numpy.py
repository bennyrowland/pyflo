import pyflo

from unittest.mock import Mock
import numpy


def test_split():
    component = pyflo.components.numpy.SplitComponent(None)
    data_port = pyflo.ports.Outport({"name": "data"})
    data_port.connect(component.inports["in"])

    target_port = pyflo.ports.Inport({"name": "target"})
    begin_mock = Mock()
    data_mock = Mock()
    end_mock = Mock()
    target_port.on('beginGroup', begin_mock)
    target_port.on('data', data_mock)
    target_port.on('endGroup', end_mock)
    component.outports["out"].connect(target_port)

    data = numpy.ones((4, 2))
    data_port.send_data(data)

    begin_mock.assert_called_once_with()
    numpy.testing.assert_almost_equal(data_mock.call_args[0][0], numpy.ones(2))
    assert data_mock.call_count == 4
    end_mock.assert_called_once_with()


def test_stack():
    component = pyflo.components.numpy.StackComponent(None)
    data_port = pyflo.ports.Outport({"name": "data"})
    data_port.connect(component.inports["in"])

    target_port = pyflo.ports.Inport({"name": "target"})
    begin_mock = Mock()
    data_mock = Mock()
    end_mock = Mock()
    target_port.on('beginGroup', begin_mock)
    target_port.on('data', data_mock)
    target_port.on('endGroup', end_mock)
    component.outports["out"].connect(target_port)

    data_port.begin_group()
    data_port.begin_group()
    data_port.send_data(numpy.arange(10))
    data_port.send_data(numpy.ones(10))
    data_port.end_group()
    data_port.end_group()

    target = numpy.stack([numpy.arange(10), numpy.ones(10)])

    begin_mock.assert_called_once_with()
    numpy.testing.assert_almost_equal(data_mock.call_args[0][0], target)
    end_mock.assert_called_once_with()


def test_stack_wait_axis():
    component = pyflo.components.numpy.StackComponent(None)
    data_port = pyflo.ports.Outport({"name": "data"})
    data_port.connect(component.inports["in"])

    axis_port = pyflo.ports.Outport({"name": "axis"})
    axis_port.connect(component.inports["axis"])

    target_port = pyflo.ports.Inport({"name": "target"})
    begin_mock = Mock()
    data_mock = Mock()
    end_mock = Mock()
    target_port.on('beginGroup', begin_mock)
    target_port.on('data', data_mock)
    target_port.on('endGroup', end_mock)
    component.outports["out"].connect(target_port)

    data_port.begin_group()
    data_port.begin_group()
    begin_mock.assert_called_once_with()
    data_port.send_data(numpy.arange(10))
    data_port.send_data(numpy.ones(10))
    data_port.end_group()
    data_port.end_group()
    end_mock.assert_not_called()
    axis_port.send_data(1)

    target = numpy.stack([numpy.arange(10), numpy.ones(10)], axis=1)

    numpy.testing.assert_almost_equal(data_mock.call_args[0][0], target)
    end_mock.assert_called_once_with()
