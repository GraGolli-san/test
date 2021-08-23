
import logging

class Node:
    def __init__ (self, id, pos):
        self.id = id
        self.pos = pos

    def __repr__ (self):
        return f'id={self.id},pos=({self.pos})'

class Link:
    def __init__ (self, id1, id2):
        self.id1 = id1
        self.id2 = id2

    def __repr__ (self):
        return f'id1={self.id1},id2={self.id2}'

class Position3d:

    def __init__ (self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__ (self):
        return f'x={self.x},y={self.y},z={self.z}'

a = 440
n = 11

b = a / n

# print(b)

nodes = []
links = []

## 四隅
id = 1
nodes.append(Node(id, Position3d(0,0,0)))
id+=1
nodes.append(Node(id, Position3d(a,0,0)))
links.append(Link(id-1,id))
id+=1
nodes.append(Node(id, Position3d(a,a,0)))
links.append(Link(id-1,id))
id+=1
nodes.append(Node(id, Position3d(0,a,0)))
links.append(Link(id-1,id))

# print(nodes)


for i in range(1,n,2):
    #print(i)
    # 上行って，右
    id+=1
    nodes.append(Node(id, Position3d(0,a - i*b,0)))
    links.append(Link(id-1,id))
    id+=1
    nodes.append(Node(id, Position3d(a - b,a - i*b,0)))
    links.append(Link(id-1,id))
    
    # 上行って，左
    id+=1
    nodes.append(Node(id, Position3d(a - b,a - (i+1)*b,0)))
    links.append(Link(id-1,id))
    id+=1
    nodes.append(Node(id, Position3d(0,a - (i+1)*b,0)))
    links.append(Link(id-1,id))


# 最後に，最初のノードとつなげる
links.append(Link(id, 1))



for n in nodes:
    # print(n)
    print(f'{n.id},{n.pos.x},{n.pos.y},{n.pos.z}')


for l in links:
    print(f'{l.id1},{l.id2}')