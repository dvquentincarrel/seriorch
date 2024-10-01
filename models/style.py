from . import record
from typing import Any, TYPE_CHECKING
from collections.abc import Iterable

class Style(record.Record):
    pages: list = []
    if TYPE_CHECKING:
        style: str
        xml_id: str
        name: str

    def __init__(self, code_field='style', ext='css'):
        self._code_attr = code_field
        self._ext = ext

    def to_dict(self, prefix) -> dict[str, Any]:
        """Transforms the record into a dictionary, omitting as many values as
        possible (values that are the same as the defaults are skipped)"""
        vals = super().to_dict(prefix, ['name'])

        if vals['name'] == vals['id']:
            del vals['name']

        return vals

    @classmethod
    def from_dict(cls, dict_: dict[str, Any], prefix: str) -> "Style":
        """Reconstructs a record from a dictionary, guessing as many values as
        possible
        :param dict_: Dictionary that describes the record
        :param prefix: Prefix of the scenario. Empty string if it's a "quirky"
            one with inconsistent ids, which means no reusable prefix
        """
        style = cls()
        style.pages = dict_.get('pages', cls.pages)

        prefix = f"{prefix}_" if not dict_.get('quirky') else ''
        style.xml_id = f"{prefix}{dict_['id']}"
        style.name = dict_.get('name') or style.xml_id

        style._incorporate_code(dict_['id'])

        return style

    @classmethod
    def from_xml(cls, node: Any) -> "Style":
        """Reconstructs a record from an xml node, guessing as many values as
        possible"""
        style = cls()
        style.xml_id = node.get('id')
        err_msg = f'La feuille CSS "{style.xml_id}" n\'a pas de balise'

        tmp = node.find('field[@name="name"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "name"')
        style.name = tmp.text

        tmp = node.find('field[@name="page_ids"]')
        if tmp is None:
            style.pages = []
        else:
            intermediate = tmp.get('eval', '')
            style.pages = record.parse_refs(intermediate)

        tmp = node.find('field[@name="style"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "style"')
        # Can contain escaped xml entities
        if not tmp.text.strip().startswith('<![CDATA['):
            style.style = record.sanitize(tmp.text.strip(), reverse=True).replace('<!CDATA[', '').replace(']]>', '')
        else:
            style.style = tmp.text.strip()

        return style

    def to_xml(self) -> str:
        """Transforms the record into a string of its XML serialization, omitting
        superfluous values
        """
        return '\n'.join(filter(lambda x: x is not None, [
            f"""    <record id="{self.xml_id}" model="ir.ui.css.ionic">""",
            f"""        <field name="name">{self.name}</field>""",
            f"""        <field name="page_ids" eval="[(6, 0, [{record.make_refs(self.pages)}])]"/>""" if self.pages else None,
            f"""        <field name="style"><![CDATA[""",
            f"""{self.style.strip()}""",
            f"""        ]]></field>""",
            f"""    </record>""",
            f"""""",
        ]))
