class Patchers(object):
    def __init__(self, patchers):
        self.__patchers = patchers

    def __enter__(self, *args, **kwargs):
        for key, value in self.__patchers.items():
            setattr(self, key, value.start())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in self.__patchers.values():
            p.stop()
