class mbsObject:
    def __init__(self,type,text):
        self.__type = type
        
        for line in text:
            splitted = line.split(":")
            if(splitted[0].strip() == "mass"): # strip = alle unnötigen Leerzeichen weg
                self.mass = float(splitted[1])