l = [1, 2, 3]
l.append("asdf")

s = set([1, 1, 2, 2, 3])

permisos = set(["perm1", "perm2"])
usuarios_1 = set(["perm2"])

permisos.add(1)
permisos.add(2)

r = permisos.difference(usuarios_1)

t = (1, 2)

t = (1, )


# lista = [x for x in range(10)]


# for x in ["hola", "mundo"]:
for _ in range(1000):
    # print(x)
    pass


def hola():
    # print("hoal")
    
    # a = open("asdasdf", "r").readlines()
    
    # with open("adasdf", "r") as f:
    #     r = f.readlines()
    #     print(r)
    #
    yield 1
    
    # print("mundo")


# for x in hola():
#     print(x)


l2 = list(hola())

g = hola()
for x in g:
    print(x)


g = hola()
for x in g:
    print(x)

# print(hola())