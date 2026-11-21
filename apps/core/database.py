from django.db import DEFAULT_DB_ALIAS, connections
from django.db.utils import Error as DatabaseError


def is_database_available(alias: str = DEFAULT_DB_ALIAS) -> bool:
    connection = connections[alias]
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        connection.close_if_unusable_or_obsolete()
        return False
    return True
