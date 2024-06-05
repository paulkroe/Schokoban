class Reward():
    def __init__(self, value, reward_type):
        self.reward_type = reward_type
        self.value = value
    
    def __repr__(self):
        return "Reward( " + str(self.value) + ", type = " + str(self.reward_type) + ")"
    
    def get_value(self):
        return self.value
    
    def get_type(self):
        return self.reward_type