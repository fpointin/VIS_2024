import mbsObject
import json


# Freedyn File öffnen
f = open("Aufgabe 2/test.fdd","r")    # r steht für read
fileContent = f.read().splitlines()         # das was auf der Festplatte steht kommt in den Arbeitsspeicher
f.close                                     # sauber arbeiten


#numOfRigidBodies = 0                        # Variablen anlegen
#numOfConstraints = 0
currentBlockType = ""
currentTextBlock = []
listOfMbsObjects = []
search4Objects = ["RIGID_BODY","CONSTRAINT"]    #mögliche Schlagwörter


for line in fileContent:                    # für alle Zeilen (line ist Iterator, alle Zeilen von Filecontent)
    if(line.find("$") >= 0):                # im fdd file ist $ immer das "Schlagwort"
        if(currentBlockType != ""):         # hier wird mit jedem Schlagwort einzeln gearbeitet, dass verschiedene Konstruktoren angewendet werden
            if(currentBlockType == "RIGID_BODY"):
                listOfMbsObjects.append(mbsObject.rigidBody(currentTextBlock))
            currentBlockType = ""

    for type_i in search4Objects:                       # Suche über alle Schlagwörter
        if(line.find(type_i,1,len(type_i)+1) >= 0):     # Position 0 ist der $, von 1 bis Länge+1 muss das RIGID_BODY stehen
            currentBlockType = type_i
            currentTextBlock.clear()
            break

    currentTextBlock.append(line)

#print('Number of rigid bodies = ',numOfRigidBodies)
#print('Number of constraints = ',numOfConstraints)


# Standard Möglichkeit, wie man ? daten/dictionarys speichern bzw lesen kann ?
modelObjects= [] #leeres array
for object in listOfMbsObjects:
    modelObjects.append(object.parameter) # man holt sich alle Parameter
jDataBase = json.dumps({"modelObjects": modelObjects})
with open("Aufgabe 2/test.json","w") as outfile:
    outfile.write(jDataBase)

f = open("Aufgabe 2/test.json","r")
data = json.load(f)
f.close()



fds = open("Aufgabe 2/test.fds","w")  # w = write
for mbsObject_i in listOfMbsObjects:
    mbsObject_i.writeInputFile(fds)
fds.close()


print(len(listOfMbsObjects))