import uuid


def is_valid_uuid(uuid_to_test, version=4):
    try:
        # Si uuid_to_test ya es un objeto UUID, no es necesario convertirlo.
        if isinstance(uuid_to_test, uuid.UUID):
            uuid_obj = uuid_to_test
        else:
            # Si uuid_to_test es una cadena, intenta convertirla a un objeto UUID.
            uuid_obj = uuid.UUID(str(uuid_to_test), version=version)

        # Compara la versión y devuelve True si coincide.
        return uuid_obj.version == version
    except ValueError:
        return False
