from random import randint
players = ['Bush', 'Zirbel', 'Reed', 'Schrade', 'Flint', 'Billy', 'Colby', 'MoP', 'TJ', 'Chip']
print(len(players))
for z in range(1,len(players)/2):
    pairing = []
    p = randint(1,len(players))
    p2 = randint(1,len(players))
    while p2 != p:
        pairing.append(players.pop(p))
        pairing.append(players.pop(p2))
        print(pairing)