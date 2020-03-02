
def funcion(uno,dos = None):
    #dos = kwargs.get('dos', None)
    if(dos==None):
        print(uno)
    else:
        print(dos+uno)
    
funcion(1,dos = 2)
funcion(1)