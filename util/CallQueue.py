
class CallQueue:
    def __init__(self, max_buffer):
        self._queue = []
        self._buffer_max = max_buffer
        self._pop_count = 0
        self._push_count = 0

    def size(self):
        return self._push_count - self._pop_count

    def pop(self):
        if self._push_count == 0 or self._push_count <= self._pop_count:
            return None
        self._pop_count += 1
        return self._queue[(self._pop_count - 1) % self._buffer_max]

    def push(self, call):
        if self._push_count < self._buffer_max:
            self._queue.append(call)
        else:
            self._queue[self._push_count % self._buffer_max] = call
        self._push_count += 1


