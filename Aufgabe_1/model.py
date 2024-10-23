import numpy as np

class Model:
    def __init__(self, iniState):
        self.state = iniState

    def get_state(self):
        return self.state
    
    def set_state(self, new_state):
        self.state = new_state

    def dydt(self, t, y):
        """Defines the system's dynamics: computes the derivative of the state vector."""
        raise NotImplementedError("This method should be implemented by subclasses.")


class SingleMassOscillator(Model):
    def __init__(self, iniState, m, k, d):
        super().__init__(iniState)
        self.m = m #Masse
        self.k = k #Steifigkeit
        self.d = 2*d*np.sqrt(self.k/self.m) #Umrechnen von D auf d

    def dydt(self, t):
        """Compute the derivatives of the state (velocity and acceleration)."""
        position = self.state[0]
        velocity = self.state[1]
        
        #position = 0.
        #velocity = 0.

        acceleration = (-self.k * position - self.d * velocity) 
        
        return np.array([velocity, acceleration]) 
        #----------------------------------------------------------------------------

