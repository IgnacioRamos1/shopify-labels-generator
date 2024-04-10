from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

import uuid


Base = declarative_base()

# Definir un tipo de columna personalizado para asegurar la compatibilidad con bases de datos que no sean PostgreSQL.
class GUID(TypeDecorator):
    """
    Plataforma independiente GUID type.

    Usa PostgreSQL's UUID type, por lo demás usa
    CHAR(32), almacenando como string hexadecimales.
    """
    impl = CHAR

    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, uuid.UUID):
            # Si el valor ya es un objeto UUID, simplemente devuélvelo
            return value
        else:
            # En caso contrario, convierte la cadena a un objeto UUID
            try:
                return uuid.UUID(value)
            except ValueError:
                # Maneja el caso en que el valor no sea un UUID válido
                return None
