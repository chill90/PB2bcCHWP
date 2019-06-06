class Motor:
    def __init__(self, name=None):
        if name is None:
            self.name = "Unnamed Motor"
        else:
            self.name = name
        
        #Public variables
        self.is_home = False
        self.is_in_pos = False
        self.is_pushing = False
        self.is_brake = False
        self.pos = 0. #mm
        #Variable to estimate the worst-case error in the position
        self.max_pos_err = 0.
        
        #Private variables, hardwired
        self.max_pos = 35. #mm
        self.min_pos = -2. #mm
        self.home_pos = -1. #mm
