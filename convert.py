import json

car = open("mini_geometry.json")

carBox = car.read()
carBox = json.loads(carBox)

car.close()

#newCar = open("mini.obj", mode = "w")

i = 0;

vert = "v "
norm = "vn "
tx = "vt "

vertData = carBox["vertexdata"]
while i < len(vertData):
    ind = i % 8
    if(ind < 3):
        vert += str(vertData[i]) + " "
    elif(ind < 6):
        norm += str(vertData[i]) + " "
    else:
        tx += str(vertData[i]) + " "

        if ind == 7:
            vert += "\nv "
            norm += "\nvn "
            tx += "\nvt "

    i += 1

vert = vert[:-2]
norm = norm[:-3]
tx = tx[:-4]
print(vert, norm, tx, sep = "\n")
