#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_utils import timeutils

from nova import objects
from nova.objects import fields
from nova.tests.unit.objects import test_objects

_ts_now = timeutils.utcnow()

_monitor_metric_spec = {
    'name': fields.MonitorMetricType.CPU_FREQUENCY,
    'value': 1000,
    'timestamp': timeutils.strtime(_ts_now),
    'source': 'nova.virt.libvirt.driver'
}

_monitor_numa_metric_spec = {
    'name': fields.MonitorMetricType.NUMA_MEM_BW_CURRENT,
    'numa_membw_values': {"0": 10, "1": 43},
    'timestamp': timeutils.strtime(_ts_now),
    'source': 'nova.virt.libvirt.driver'
}

_monitor_metric_list_spec = [_monitor_metric_spec]


class _TestMonitorMetricObject(object):
    def test_monitor_metric_to_dict(self):
        obj = objects.MonitorMetric(name='cpu.frequency',
                                    value=1000,
                                    timestamp=_ts_now,
                                    source='nova.virt.libvirt.driver')
        self.assertEqual(_monitor_metric_spec, obj.to_dict())

    def test_monitor_metric_list_to_list(self):
        obj = objects.MonitorMetric(name='cpu.frequency',
                                    value=1000,
                                    timestamp=_ts_now,
                                    source='nova.virt.libvirt.driver')
        list_obj = objects.MonitorMetricList(objects=[obj])
        self.assertEqual(_monitor_metric_list_spec, list_obj.to_list())

    def test_monitor_NUMA_metric_to_dict(self):
        obj = objects.MonitorMetric(name='numa.membw.current',
                                    numa_membw_values={"0": 10, "1": 43},
                                    timestamp=_ts_now,
                                    source='nova.virt.libvirt.driver')
        self.assertEqual(_monitor_numa_metric_spec, obj.to_dict())


class TestMonitorMetricObject(test_objects._LocalTest,
                              _TestMonitorMetricObject):
    pass


class TestRemoteMonitorMetricObject(test_objects._RemoteTest,
                                    _TestMonitorMetricObject):
    pass
