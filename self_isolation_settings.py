class SelfIsolationSetting:
    def __init__(self, *args, **kwargs):
        self.self_isolate_proportion = kwargs.get('self_isolate_proportion', 0.6)
        self.isolation_bounds = kwargs.get('isolation_bounds', [0.02, 0.02, 0.1, 0.98])

    def get(self, key):
        '''gets key value from config'''
        try:
            return self.__dict__[key]
        except:
            raise Exception('key %s not present in config' % key)

    def set(self, key, value):
        '''sets key value in config'''
        self.__dict__[key] = value