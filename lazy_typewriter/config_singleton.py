class _SysConfig():
    _instance = None 
    def __new__(cls, *args, **kwargs): 
        if cls._instance is None: 
            cls._instance = super().__new__(cls) 
        return cls._instance 

    def __init__(self): 
        self.pin = True 
        self.vm_mode = True
        self.slow_mode = False
        self.slow_mode_time = 0.05

sys_config = _SysConfig()