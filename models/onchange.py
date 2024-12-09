from . import record
from lxml import etree
from typing import Any, TYPE_CHECKING
from collections.abc import Iterable

class Onchange(record.Record):
    deprecated: bool = False
    raw: bool = True
    secure: bool = True
    translatable = None
    model_id: str = 'manual.onchange'
    if TYPE_CHECKING:
        code: str
        xml_id: str
        name: str

    def __init__(self, code_field='code', ext='py'):
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
    def from_dict(cls, dict_: dict[str, Any], prefix: str) -> "Onchange":
        """Reconstructs a record from a dictionary, guessing as many values as
        possible
        :param dict_: Dictionary that describes the record
        :param prefix: Prefix of the scenario. Empty string if it's a "quirky"
            one with inconsistent ids, which means no reusable prefix
        """
        onchange = cls()
        onchange.deprecated = dict_.get('deprecated', cls.deprecated)
        onchange.raw = dict_.get('raw', cls.raw)
        onchange.secure = dict_.get('secure', cls.secure)
        onchange.translatable = dict_.get('translatable', cls.translatable)
        onchange.model_id = dict_.get('model_id', cls.model_id)

        prefix = f"{prefix}_" if not dict_.get('quirky') else ''
        onchange.xml_id = f"{prefix}{dict_['id']}"
        onchange.name = dict_.get('name') or onchange.xml_id

        onchange._incorporate_code(dict_['id'])

        return onchange

    @classmethod
    def from_xml(cls, node: Any) -> "Onchange":
        """Reconstructs a record from an xml node, guessing as many values as
        possible"""
        onchange = cls()
        onchange.xml_id = node.get('id')
        err_msg = f'L\'onchange "{onchange.xml_id}" n\'a pas de balise'

        tmp = node.find('field[@name="name"]')
        if tmp is None:
            onchange.name = node.get('id')
        else:
            onchange.name = tmp.text

        tmp = node.find('field[@name="raw_code"]')
        if tmp is not None:
            onchange.raw = True
        else:
            tmp = node.find('field[@name="code"]')
            if tmp is None:
                raise ValueError(f'{err_msg} "code" ou "raw_code"')
            onchange.raw = False

        # No sanitizing (getting it right in all cases is headache-inducing, fuck it.)
        onchange.code = tmp.text.strip()

        tmp = node.find('field[@name="is_deprecated"]')
        if tmp is None:
            onchange.deprecated = cls.deprecated
        else:
            # Bool-wrapped because sometimes it's an int 🤡
            onchange.deprecated = bool(eval(tmp.get('eval', 'False')))

        tmp = node.find('field[@name="is_security_check"]')
        if tmp is None:
            onchange.secure = cls.secure
        else:
            onchange.secure = bool(eval(tmp.get('eval', 'False')))

        tmp = node.find('field[@name="is_translatable_code"]')
        if tmp is None:
            onchange.translatable = cls.translatable
        else:
            intermediate = eval(tmp.get('eval'))
            if intermediate is not None:
                onchange.translatable = bool(intermediate)
            else:
                onchange.translatable = None

        # Évalue le domaine de recherche pour obtenir le nom du modèle
        tmp = node.find('field[@name="model_id"]')
        if tmp is None:
            onchange.model_id = cls.model_id
        else:
            model_str = tmp.get('search')
            if not model_str:
                onchange.model_id = cls.model_id
            else:
                value: Any | list[tuple[str, str, str]] = eval(model_str)
                search_err_msg = f"L'onchange {onchange.xml_id} a un modèle d'une autre forme que \"[('model', '=', 'NOM.DU.MODÈLE')]\""
                if not isinstance(value, Iterable) or len(value) != 1:
                    raise ValueError(search_err_msg)
                elif not isinstance(value[0], Iterable) or len(value[0]) != 3:
                    raise ValueError(search_err_msg)
                onchange.model_id = value[0][-1]

        return onchange

    def to_xml(self) -> str:
        """Transforms the record into a string of its XML serialization, omitting
        superfluous values
        """
        return '\n'.join(filter(lambda x: x is not None, [
            f"""    <record id="{self.xml_id}" model="manual.onchange">""",
            f"""        <field name="name">{self.name}</field>""",
            f"""        <field name="model_id" search="[('model', '=', '{self.model_id}')]"/>""",
            f"""        <field name="is_deprecated" eval="{self.deprecated}"/>""" if self.deprecated else None,
            f"""        <field name="is_translatable_code" eval="{self.translatable}"/>""" if self.translatable is not None else None,
            f"""        <field name="is_security_check" eval="{self.secure}"/>""" if not self.secure else None,
            f"""        <field name="{'raw_' * self.raw}code"><![CDATA[""",
            f"""{self.code.strip()}""",
            f"""        ]]></field>""",
            f"""    </record>""",
            f"""""",
        ]))

    def inject(self, cursor: Any) -> None:
        """Injects onchange's architecture in the DB. Does not commit

        :param cursor: Database cursor
        """
        code = self.code.replace("'", "''")
        cursor.execute(f"""
            UPDATE manual_onchange
            SET {'raw_' if self.raw else ''}code = '{code}',
                is_translatable_code = '{bool(self.translatable)}'
            WHERE name = '{self.name}'
        """)
