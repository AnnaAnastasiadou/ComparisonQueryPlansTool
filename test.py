class Obj():
    item = 0


a = Obj()
a.item = 1


lst = [a]

lst[0].item = 2

print(a.item)