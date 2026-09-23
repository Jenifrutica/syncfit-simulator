from syncfit_simulator.generator import generate_frame
from syncfit_simulator.scenarios import get_scenario
from syncfit_simulator.structures import EventScript, FrameBuffer


def test_frame_buffer_reuses_ring_buffer():
    buffer = FrameBuffer(capacity=2)
    buffer.push({"id": 1})
    buffer.push({"id": 2})
    buffer.push({"id": 3})
    assert len(buffer) == 2
    assert buffer.latest() == {"id": 3}
    assert buffer.to_list() == [{"id": 2}, {"id": 3}]


def test_frame_buffer_with_generated_frames():
    buffer = FrameBuffer(capacity=8)
    for i in range(3):
        buffer.push(generate_frame(get_scenario("normal"), session_id="sid", frame_index=i))
    assert len(buffer) == 3
    assert buffer.latest()["session_id"] == "sid"


def test_event_script_fifo():
    script = EventScript()
    script.add(0.0, "start")
    script.add(1.0, "peak")
    assert len(script) == 2
    assert script.next() == (0.0, "start", {})
    assert script.next() == (1.0, "peak", {})
    assert script.next() is None
