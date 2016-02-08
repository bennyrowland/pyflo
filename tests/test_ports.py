import pyflo.ports

import pytest
from unittest.mock import Mock


def test_invalid_event_type():
    port = pyflo.ports.Inport({"name": "test"})
    with pytest.raises(KeyError):
        port.on('dummy', print)


def test_decorator():
    port = pyflo.ports.Inport({"name": "test"})
    mock = Mock()

    @port.on("data")
    def some_function(data):
        mock(data)

    port.data("data")

    mock.assert_called_once_with("data")


def test_connect():
    inport = pyflo.ports.Inport({"name": "in"})
    mock = Mock()
    inport.on('connect', mock)
    outport = pyflo.ports.Outport({"name": "out"})

    outport.connect(inport)
    assert inport in outport.listeners
    mock.assert_called_once_with()
    assert inport.attached()


def test_begin_end_group():
    inport = pyflo.ports.Inport({"name": "in"})
    mock = Mock()
    mock2 = Mock()
    inport.on('beginGroup', mock)
    inport.on('endGroup', mock2)
    outport = pyflo.ports.Outport({"name": "out"})

    outport.connect(inport)
    outport.begin_group()
    mock.assert_called_once_with()
    mock2.assert_not_called()
    outport.end_group()
    mock2.assert_called_once_with()


def test_send_data():
    inport = pyflo.ports.Inport({"name": "in"})
    mock = Mock()
    inport.on('data', mock)
    outport = pyflo.ports.Outport({"name": "out"})

    outport.connect(inport)
    outport.send_data("data")
    mock.assert_called_once_with("data")


def test_disconnect():
    inport = pyflo.ports.Inport({"name": "in"})
    mock = Mock()
    inport.on('disconnect', mock)
    outport = pyflo.ports.Outport({"name": "out"})

    outport.connect(inport)
    outport.disconnect()
    mock.assert_called_once_with()


def test_pass_through():
    external_port = pyflo.ports.Outport({"name": "out"})
    ptp = pyflo.ports.PassThroughPort({"name": "pass"})
    internal_port = pyflo.ports.Inport({"name"})

    mock = Mock()
    internal_port.on("data", mock)

    external_port.connect(ptp)
    ptp.connect(internal_port)

    external_port.send_data("data")
    mock.assert_called_once_with("data")