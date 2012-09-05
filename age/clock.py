import sfml as sf
import sys
import time
from collections import deque
from threading import Timer

import logging as log

class ScheduledItem(object):
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

class ScheduledIntervalItem(object):
    def __init__(self, func, interval, last_ts, next_ts, args, kwargs):
        self.func = func
        self.interval = interval
        self.last_ts = last_ts
        self.next_ts = next_ts
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return "{0}".format(self.func)

class GameClock(sf.Clock):

    def __init__(self):
        super(GameClock, self).__init__()
        if sys.platform in ('win32', 'cygwin'):
            self.time = time.clock
        else:
            self.time = time.time

        self.frame = 0
        self.fpses = deque()
        self.ticks = deque()
        self.fps = 0
        self.average_fps = 0
        self.started = self.time()
        self.last_ts = self.started
        
        self.scheduled_items = list()
        self.scheduled_interval_items = list()

    def update(self):
        self.frame += 1
        ts = self.time()
        dt = sf.Time(seconds=ts - self.last_ts)
        
        to_remove = list()

        for item in self.scheduled_items:
            item.func(dt, *item.args, **item.kwargs)

        for item in self.scheduled_interval_items:
            if ts >= item.next_ts:
                #log.debug("Event fired, time since last run: {0}".format(ts - item.last_ts))
                if ts - item.next_ts >= 0.01:
                    log.debug("Event missed by a lot. Difference was:{0}".format(ts - item.next_ts))
                item.func(dt, *item.args, **item.kwargs)
                if item.interval > 0:
                    item.last_ts = ts
                    item.next_ts = ts + item.interval
                else:
                    to_remove.append(item)

        for item in to_remove:
            self.scheduled_interval_items.remove(item)
        
        self.restart()
        self.last_ts = ts
        self.ticks.append(dt)
        while len(self.ticks) > 1000:
            self.ticks.popleft()

        return dt

    def calculate_fps(self, dt):
        total_frame_time = sum(t.as_seconds() for t in self.ticks)
        if total_frame_time <= 0: 
            self.fps = 0
        else:
            self.fps = int(len(self.ticks) / total_frame_time)
        self.fpses.append(self.fps)
        while len(self.fpses) > 1000:
            self.fpses.popleft()
        self.average_fps = int(sum(self.fpses) / len(self.fpses))

    def sort_scheduled_interval_items(self):
        self.scheduled_interval_items.sort(key=lambda a: a.next_ts)

    def schedule(self, func, *args, **kwargs):
        self.scheduled_items.append(ScheduledItem(func, args, kwargs))

    def _schedule_item(self, func, last_ts, next_ts, interval, *args, **kwargs):
        self.scheduled_interval_items.append(
                ScheduledIntervalItem(func, interval, last_ts, next_ts, args, kwargs))


    def schedule_interval(self, func, interval, *args, **kwargs):
        last_ts = self.last_ts
        next_ts = last_ts + interval
        self._schedule_item(func, last_ts, next_ts, interval, *args, **kwargs)
        self.sort_scheduled_interval_items()

    def schedule_once(self, func, delay, *args, **kwargs):
        last_ts = self.last_ts
        next_ts = last_ts + delay
        self._schedule_item(func, last_ts, next_ts, 0, *args, **kwargs)
        self.sort_scheduled_interval_items()

    def unschedule(self, func):
        self.scheduled_items = [item for item in self.scheduled_items if item.func <> func]
        self.scheduled_interval_items = [item for item in self.scheduled_interval_items if item.func <> func]

