import logging
import typing as tp
from satella.instrumentation.memory import MemoryPressureManager, CustomCondition, All, Any
import time
import unittest
logger = logging.getLogger(__name__)


class OnDemandCondition(CustomCondition):
    def __init__(self):
        self.value = False
        super().__init__(lambda: self.value)

    def can_fire(self, *args) -> bool:
        return self.value


class TestMemory(unittest.TestCase):
    def test_memory(self):
        odc = OnDemandCondition()

        a = {'memory': False,
             'calls': 0,
             'improved': False,
             'times_entered_1': 0,
             'level_2_engaged': False,
             'level_2_confirmed': False,
             'cancelled': 0,
             'mem_normal': 0}

        cc = CustomCondition(lambda: a['level_2_engaged'])

        MemoryPressureManager(None, [odc, All(cc, Any(cc, cc))], 2)

        def memory_normal():
            nonlocal a
            a['mem_normal'] += 1

        def cancel():
            nonlocal a
            a['cancelled'] += 1
        MemoryPressureManager.register_on_memory_normal(memory_normal)

        cc = MemoryPressureManager.register_on_entered_severity(1)(cancel)

        @MemoryPressureManager.register_on_entered_severity(2)
        def call_on_level_2():
            a['level_2_confirmed'] = True

        @MemoryPressureManager.register_on_remaining_in_severity(1)
        def call_on_memory_still():
            a['calls'] += 1

        @MemoryPressureManager.register_on_entered_severity(1)
        def call_on_no_memory():
            a['memory'] = True
            a['times_entered_1'] += 1

        @MemoryPressureManager.register_on_left_severity(1)
        def call_improved():
            a['improved'] = True

        self.assertFalse(a['memory'])
        self.assertFalse(a['improved'])
        self.assertEqual(a['mem_normal'], 0)
        time.sleep(3)
        odc.value = True
        time.sleep(5)
        self.assertEqual(a['cancelled'], 1)
        cc.cancel()
        self.assertTrue(a['memory'])
        self.assertFalse(a['improved'])
        self.assertGreater(a['calls'], 0)
        self.assertEqual(a['times_entered_1'], 1)
        odc.value = False
        time.sleep(3)
        self.assertTrue(a['improved'])
        self.assertEqual(a['times_entered_1'], 1)
        self.assertTrue(a['memory'])
        self.assertEqual(a['mem_normal'], 1)
        a['level_2_engaged'] = True
        time.sleep(3)
        self.assertEqual(MemoryPressureManager().severity_level, 2)
        self.assertEqual(a['cancelled'], 1)
        self.assertEqual(a['times_entered_1'], 2)
        self.assertTrue(a['level_2_confirmed'])
        self.assertEqual(a['mem_normal'], 1)
