from . import param
from typing import Any, TYPE_CHECKING

class Label(param.Param):
    if TYPE_CHECKING:
        xml_id: str
        name: str
        value: str

    def to_dict(self, prefix) -> dict[str, Any]:
        """Transforms the record into a dictionary, omitting as many values as
        possible (values that are the same as the defaults are skipped)"""
        vals = super().to_dict(prefix)
        del vals['note']
        return vals

    def to_xml(self, prefix: str) -> str:
        """Transforms the record into a string of its XML serialization, omitting
        superfluous values
        """
        return super().to_xml(prefix).replace('ir.ui.menu.ionic.param', 'ir.ui.menu.ionic.label')
