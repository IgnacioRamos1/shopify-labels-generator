from manual_store import Store


def seleccionar_tienda(session):
    tiendas = session.query(Store).all()
    for indice, tienda in enumerate(tiendas, start=1):
        print(f"{indice}. {tienda.name} (ID: {tienda.id})")

    seleccion = int(input("Selecciona el número de la tienda a la que pertenece el producto: "))
    tienda_seleccionada = tiendas[seleccion - 1]  # Ajusta según la selección del usuario
    return tienda_seleccionada.id
    