import abc


class Observable(object):
    __metaclass__ = abc.ABCMeta

    _observers = set()

    add_observer = _observers.add
    remove_observer = _observers.remove
    clear_observers = _observers.clear

    def notify_obervers(self, f_name, cls, *f_args):
        for observer in self._observers:
            if isinstance(observer, cls):
                func = getattr(observer, f_name)
                func(*f_args)
