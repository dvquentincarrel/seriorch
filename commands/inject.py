from typing import Any
from models import utils

def inject(config: dict[str, Any]) -> None:
    """Injects the data of the records in the DB. The records must already exist"""
    _, onchanges, views, styles, labels, params = utils.rebuild_models('skeleton.yaml')
    cursor = utils.get_db_cursor(config)
    inject_ = lambda rcs: [rc.inject(cursor) for rc in rcs]
    [inject_(records) for records in [onchanges, views, styles, labels, params]]
    cursor.connection.commit()
