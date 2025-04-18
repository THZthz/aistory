from typing import Callable
import traceback

from aistory.db.connection import Connection, ConnectionSingletonClass


def safe_transactions(prompts: str, action: Callable):
    conn = Connection().connection

    try:
        with conn.cursor() as cursor:
            res = action(cursor)

        conn.commit()
        return res

    except Exception as e:
        print(f'''--- {type(e).__name__} when {prompts}: {e}''')

        traceback.print_exc()

        conn.rollback()

