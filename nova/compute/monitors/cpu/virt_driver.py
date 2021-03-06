# Copyright 2013 Intel Corporation.
# All Rights Reserved.
#
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

"""
CPU monitor based on virt driver to retrieve CPU information
"""

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import timeutils

from nova.compute.monitors import base
from nova import exception
from nova.i18n import _LE

CONF = cfg.CONF
CONF.import_opt('compute_driver', 'nova.virt.driver')
LOG = logging.getLogger(__name__)


class Monitor(base.CPUMonitorBase):
    """CPU monitor that uses the virt driver's get_host_cpu_stats() call."""

    def __init__(self, resource_tracker):
        super(Monitor, self).__init__(resource_tracker)
        self.source = CONF.compute_driver
        self.driver = resource_tracker.driver
        self._data = {}
        self._cpu_stats = {}

    def get_metric(self, name):
        self._update_data()
        return self._data[name], self._data["timestamp"]

    def _update_data(self):
        # Don't allow to call this function so frequently (<= 1 sec)
        now = timeutils.utcnow()
        if self._data.get("timestamp") is not None:
            delta = now - self._data.get("timestamp")
            if delta.seconds <= 1:
                return

        self._data = {}
        self._data["timestamp"] = now

        # Extract node's CPU statistics.
        try:
            stats = self.driver.get_host_cpu_stats()
            self._data["cpu.user.time"] = stats["user"]
            self._data["cpu.kernel.time"] = stats["kernel"]
            self._data["cpu.idle.time"] = stats["idle"]
            self._data["cpu.iowait.time"] = stats["iowait"]
            self._data["cpu.frequency"] = stats["frequency"]
        except (NotImplementedError, TypeError, KeyError):
            LOG.exception(_LE("Not all properties needed are implemented "
                              "in the compute driver"))
            raise exception.ResourceMonitorError(
                monitor=self.__class__.__name__)

        # The compute driver API returns the absolute values for CPU times.
        # We compute the utilization percentages for each specific CPU time
        # after calculating the delta between the current reading and the
        # previous reading.
        stats["total"] = (stats["user"] + stats["kernel"]
                          + stats["idle"] + stats["iowait"])
        cputime = float(stats["total"] - self._cpu_stats.get("total", 0))

        perc = (stats["user"] - self._cpu_stats.get("user", 0)) / cputime
        self._data["cpu.user.percent"] = perc

        perc = (stats["kernel"] - self._cpu_stats.get("kernel", 0)) / cputime
        self._data["cpu.kernel.percent"] = perc

        perc = (stats["idle"] - self._cpu_stats.get("idle", 0)) / cputime
        self._data["cpu.idle.percent"] = perc

        perc = (stats["iowait"] - self._cpu_stats.get("iowait", 0)) / cputime
        self._data["cpu.iowait.percent"] = perc

        # Compute the current system-wide CPU utilization as a percentage.
        used = stats["user"] + stats["kernel"] + stats["iowait"]
        prev_used = (self._cpu_stats.get("user", 0)
                     + self._cpu_stats.get("kernel", 0)
                     + self._cpu_stats.get("iowait", 0))
        perc = (used - prev_used) / cputime
        self._data["cpu.percent"] = perc

        self._cpu_stats = stats.copy()
