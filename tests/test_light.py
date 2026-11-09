import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from app.sensors.light.light import Light, persist_light_state


class TestLight(unittest.TestCase):
    @patch("app.sensors.light.light.PWMLED")
    @patch("app.sensors.light.light.PiGPIOFactory")
    @patch("app.sensors.light.light.pigpio.pi")
    def setUp(self, MockPi, MockFactory, MockPWMLED):
        self.mock_led = MockPWMLED.return_value
        self.mock_led.value = 0
        self.mock_pi = MockPi.return_value
        self.light = Light(18)

    def test_turn_on_from_0(self):
        self.mock_led.value = 0
        self.light.on()
        self.assertEqual(self.mock_led.value, 1)
        self.assertLogs("Turning light on")

    def test_turn_on_from_nonzero(self):
        self.mock_led.value = 0.5
        self.light.on()
        self.assertEqual(self.mock_led.value, 0.5)
        self.assertLogs("Light already on, skipping")

    def test_off(self):
        self.mock_led.value = 1
        self.light.off()
        self.assertEqual(self.mock_led.value, 0)
        self.assertLogs("Turning light off")

    def test_set_brightness_valid(self):
        valid_brightness = 70
        self.light.set_brightness(valid_brightness)
        self.assertEqual(self.mock_led.value * 100, valid_brightness)

    def test_set_brightness_invalid(self):
        with self.assertRaises(ValueError):
            self.light.set_brightness(110)

    def test_set_frequency(self):
        freq = 10000  # 10kHz
        self.light.set_frequency(freq)
        self.mock_pi.set_PWM_frequency.assert_called_with(18, freq)

    def test_close(self):
        self.light.close()
        self.mock_led.close.assert_called_once()



class TestPersistLightState(unittest.TestCase):
    """The cron `light` command must record where it left the light, so a restart restores it."""

    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(self.path)
        patcher = patch.object(config, "STATE_FILE", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(lambda: os.path.exists(self.path) and os.unlink(self.path))

    def saved(self):
        with open(self.path) as fh:
            return json.load(fh)

    def test_on_saves_level(self):
        persist_light_state(MagicMock(get_brightness=lambda: 100.0))
        self.assertEqual(self.saved()["light_on"], True)
        self.assertEqual(self.saved()["brightness"], 100)

    def test_off_saves_off_and_keeps_last_brightness(self):
        persist_light_state(MagicMock(get_brightness=lambda: 80.0))
        persist_light_state(MagicMock(get_brightness=lambda: 0.0))
        self.assertEqual(self.saved()["light_on"], False)
        self.assertEqual(self.saved()["brightness"], 80)


if __name__ == "__main__":
    unittest.main()
