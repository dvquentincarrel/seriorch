from . import record
from typing import Any, TYPE_CHECKING
import lxml.etree as etree
from collections.abc import Iterable

class View(record.Record):

    deprecated: bool = False
    raw: bool = True
    secure: bool = True
    trans: None | bool = None
    model_id: str = 'ir.ui.view.ionic'
    inherit: str = ''
    name: str = 'Accueil'
    if TYPE_CHECKING:
        arch: str
        xml_id: str
        identifier: str

    def __init__(self, code_field='arch', ext='xml'):
        self._code_attr = code_field
        self._ext = ext

    def to_dict(self, prefix) -> dict[str, Any]:
        """Transforms the record into a dictionary, omitting as many values as
        possible (values that are the same as the defaults are skipped)"""
        vals = super().to_dict(prefix, ['identifier'])

        if vals['identifier'] == vals['id']:
            del vals['identifier']

        return vals

    @classmethod
    def from_dict(cls, dict_: dict[str, Any], prefix: str) -> "View":
        """Reconstructs a record from a dictionary, guessing as many values as
        possible
        :param dict_: Dictionary that describes the record
        :param prefix: Prefix of the scenario. Empty string if it's a "quirky"
            one with inconsistent ids, which means no reusable prefix
        """
        view = cls()
        view.deprecated = dict_.get('deprecated', cls.deprecated)
        view.raw = dict_.get('raw', cls.raw)
        view.secure = dict_.get('secure', cls.secure)
        view.trans = dict_.get('translatable', cls.trans)
        view.model_id = dict_.get('model_id', cls.model_id)
        view.inherit = dict_.get('inherit', cls.inherit)
        view.name = dict_.get('name', cls.name)

        prefix = f"{prefix}_" if not dict_.get('quirky') else ''
        view.xml_id = f"{prefix}{dict_['id']}"
        view.identifier = dict_.get('identifier') or view.xml_id

        view._incorporate_code(dict_['id'])

        return view

    @classmethod
    def from_xml(cls, node: Any) -> "View":
        """Reconstructs a record from an xml node, guessing as many values as
        possible"""
        view = cls()
        view.xml_id = node.get('id')
        err_msg = f'La vue "{view.xml_id}" n\'a pas de balise'

        tmp = node.find('field[@name="identifier"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "identifier"')
        view.identifier = tmp.text

        tmp = node.find('field[@name="name"]')
        if tmp is None:
            view.name = cls.name
        else:
            view.name = tmp.text

        tmp = node.find('field[@name="raw_architecture"]')
        if tmp is not None:
            view.raw = True
        else:
            tmp = node.find('field[@name="architecture"]')
            if tmp is None:
                raise ValueError(f'{err_msg} "architecture" ou "raw_architecture"')
            view.raw = False
        view.arch = etree.tostring(tmp.find('data'), encoding="unicode")

        tmp = node.find('field[@name="is_deprecated"]')
        if tmp is None:
            view.deprecated = cls.deprecated
        else:
            view.deprecated = bool(eval(tmp.get('eval', 'False')))

        tmp = node.find('field[@name="is_security_check"]')
        if tmp is None:
            view.secure = cls.secure
        else:
            view.secure = bool(eval(tmp.get('eval', 'False')))

        # Évalue le domaine de recherche pour obtenir le nom du modèle
        tmp = node.find('field[@name="model_id"]')
        if tmp is None:
            view.model_id = cls.model_id
        else:
            model_str = tmp.get('search')
            if not model_str:
                view.model_id = cls.model_id
            else:
                value: Any | list[tuple[str, str, str]] = eval(model_str)
                search_err_msg = f"La vue {view.xml_id} a un modèle d'une autre forme que \"[('model', '=', 'NOM.DU.MODÈLE')]\""
                if not isinstance(value, Iterable) or len(value) != 1:
                    raise ValueError(search_err_msg)
                elif not isinstance(value[0], Iterable) or len(value[0]) != 3:
                    raise ValueError(search_err_msg)
                view.model_id = value[0][-1]

        tmp = node.find('field[@name="inherited_view_id"]')
        if tmp is None:
            view.inherit = cls.inherit
        else:
            view.inherit = view.get_ref(tmp)

        tmp = node.find('field[@name="is_translatable_architecture"]')
        if tmp is None:
            view.trans = cls.trans
        else:
            intermediate = eval(tmp.get('eval'))
            if intermediate is not None:
                view.trans = bool(intermediate)
            else:
                view.trans = None

        return view

    def to_xml(self) -> str:
        """Transforms the record into a string of its XML serialization, omitting
        superfluous values
        """
        return '\n'.join(filter(lambda x: x is not None, [
            f"""    <record id="{self.xml_id}" model="ir.ui.view.ionic">""",
            f"""        <field name="identifier">{self.identifier}</field>""",
            f"""        <field name="name">{self.name}</field>""",
            f"""        <field name="inherited_view_id" ref="{self.inherit}"/>""" if self.inherit else None,
            f"""        <field name="model_id" search="[('model', '=', '{self.model_id}')]"/>""",
            f"""        <field name="is_translatable_architecture" eval="{not self.trans}"/>""" if self.trans is not None else None,
            f"""        <field name="is_security_check" eval="{self.secure}"/>""" if not self.secure else None,
            f"""        <field name="is_deprecated" eval="{self.deprecated}"/>""" if self.deprecated else None,
            f"""        <field name="{'raw_' * self.raw}architecture" type="xml">""",
            f"""{self.arch.strip()}""",
            f"""        </field>""",
            f"""    </record>""",
            f"""""",
        ]))

