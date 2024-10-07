from . import record
from typing import Any, TYPE_CHECKING
from collections.abc import Iterable

class Param(record.Record):
    note: str = ''
    if TYPE_CHECKING:
        xml_id: str
        name: str
        value: str

    def to_dict(self, prefix) -> dict[str, Any]:
        """Transforms the record into a dictionary, omitting as many values as
        possible (values that are the same as the defaults are skipped)"""
        vals = super().to_dict(prefix, [])

        if vals['name'] == vals['id']:
            del vals['name']

        return vals

    @classmethod
    def from_dict(cls, dict_: dict[str, Any], prefix: str) -> "Param":
        """Reconstructs a record from a dictionary, guessing as many values as
        possible
        :param dict_: Dictionary that describes the record
        :param prefix: Prefix of the scenario. Empty string if it's a "quirky"
            one with inconsistent ids, which means no reusable prefix
        """
        param = cls()
        param.value = record.sanitize(dict_.get('value', ''), light=True)
        param.note = dict_.get('note', cls.note)

        prefix = f"{prefix}_" if not dict_.get('quirky') else ''
        param.xml_id = f"{prefix}{dict_['id']}"
        param.name = dict_.get('name') or dict_['id']

        return param

    @classmethod
    def from_xml(cls, node: Any) -> "Param":
        """Reconstructs a record from an xml node, guessing as many values as
        possible"""
        param = cls()
        param.xml_id = node.get('id')
        err_msg = f'Le paramètre "{param.xml_id}" n\'a pas de balise'

        tmp = node.find('field[@name="name"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "name"')
        param.name = tmp.text.strip()

        tmp = node.find('field[@name="value"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "value"')
        param.value = record.sanitize(tmp.text.strip(), reverse=True, light=True)


        tmp = node.find('field[@name="note"]')
        if tmp is None:
            param.note = cls.note
        else:
            param.note = tmp.text

        return param

    def to_xml(self, prefix: str) -> str:
        """Transforms the record into a string of its XML serialization, omitting
        superfluous values
        """
        return '\n'.join(filter(lambda x: x is not None, [
            f"""    <record id="{self.xml_id}" model="ir.ui.menu.ionic.param">""",
            f"""        <field name="name">{self.name}</field>""",
            f"""        <field name="ionic_menu_id" eval="ref('{prefix}')"/>""",
            f"""        <field name="value">{self.value}</field>""",
            f"""        <field name="note">{self.note}</field>""" if self.note else None,
            f"""    </record>""",
            f"""""",
        ]))

    def inject(self, cursor: Any) -> None:
        """Injects param's value in the DB. Does not commit
        TODO: Filter on xml id. It would overwrite ALL params with this name

        :param cursor: Database cursor
        """
        value = self.value.replace("'", "''")
        cursor.execute(f"""
            UPDATE ir_ui_menu_ionic_param
            SET value = '{value}'
            WHERE name = '{self.name}'
        """)
