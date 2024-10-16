"""Representation & manipulation of a scenario entry.
Does NOT handle the case of modifications of external scenarios
(adding onchanges/views, changing the initial onchange/view)
"""

from . import record
from typing import Any, TYPE_CHECKING, Optional

class Scenario(record.Record):
    no_cache: Optional[bool] = None
    deprecated: Optional[bool] = None
    parent: Optional[str] = None
    help: Optional[str] = None
    init_oc: Optional[str] = None
    if TYPE_CHECKING:
        xml_id: str
        file_name: str # Allow handling of cases where xml_id doesn't reflect data file name
        name: str
        icon: str
        seq: str
        main_view: str
        views: list[str]
        styles: list[str]
        onchanges: list[str]

    def to_dict(
        self,
        new_onchanges: list[str],
        new_views: list[str],
        new_styles: list[str],
    ) -> dict[str, Any]:
        """Transforms the record into a dictionary, omitting as many values as
        possible (values that are the same as the defaults are skipped)

        :param new_onchanges: Name of the onchanges added by the scenario
        :param new_views: Name of the views added by the scenario
        :param new_styles: Name of the css pages added by the scenario
        """
        # Trick to get it to show up first in the yaml output, since dicts
        # are insert-order--ordered now
        vals = {'prefix': self.xml_id}
        # Strips prefix from oc/views/styles. Further pruning to distinguish
        # between external/here-defined entries is required
        suffix = lambda x: x.replace(f'{self.xml_id}_', '')

        other_onchanges = [suffix(record) for record in set(self.onchanges) - set(new_onchanges)]
        if other_onchanges:
            vals['other_onchanges'] = other_onchanges

        other_views = [suffix(record) for record in set(self.views) - set(new_views)]
        if other_views:
            vals['other_views'] = other_views

        other_styles = [suffix(record) for record in set(self.styles) - set(new_styles)]
        if other_styles:
            vals['other_styles'] = other_styles

        # Handle cases were the records come from outside or are badly named
        if self.main_view.startswith(self.xml_id):
            self.main_view = suffix(self.main_view)
        else:
            self.quirky_main_view = self.main_view
            delattr(self, 'main_view')

        if self.init_oc.startswith(self.xml_id):
            self.init_oc = suffix(self.init_oc)
        else:
            self.quirky_init_oc = self.init_oc
            delattr(self, 'init_oc')

        _vals = super().to_dict(None, None)
        del _vals['id']
        vals.update(_vals)

        return vals

    @classmethod
    def from_dict(cls, dict_: dict[str, Any]) -> "Scenario":
        """Reconstructs a record from a dictionary, guessing as many values as
        possible

        :param dict_: Dictionary that describes the record
        """
        menu = cls()
        menu.xml_id = dict_['prefix']
        menu.file_name = dict_.get('file_name', menu.xml_id)
        menu.name = dict_['name']
        menu.icon = dict_['icon']
        menu.seq = dict_['sequence']
        # Quirky versions either come from outside or were badly named
        menu.main_view = dict_.get('quirky_main_view') or f"{menu.xml_id}_{dict_['main_view']}"
        menu.init_oc = dict_.get('quirky_init_oc') or f"{menu.xml_id}_{dict_['init_oc']}"

        menu.no_cache = dict_.get('no_cache')
        menu.deprecated = dict_.get('deprecated')
        menu.parent = dict_.get('parent')
        menu.help = dict_.get('help')

        # Aggregate external & here-defined records
        menu.styles = dict_.get('other_styles', [])
        menu.styles.extend(
            [f"{menu.xml_id}_{style['id']}" for style in dict_.get('styles', [])])

        menu.onchanges = dict_.get('other_onchanges', [])
        menu.onchanges.extend(
            [f"{menu.xml_id}_{onchange['id']}" for onchange in dict_.get('onchanges', [])])

        menu.views = dict_.get('other_views', [])
        menu.views.extend(
            [f"{menu.xml_id}_{view['id']}" for view in dict_.get('views', [])])

        return menu

    @classmethod
    def from_xml(cls, node: Any) -> "Scenario":
        """Reconstructs a record from an xml node, guessing as many values as
        possible"""
        menu = cls()
        menu.xml_id = node.get('id')
        err_msg = f'Le scénario "{menu.xml_id}" n\'a pas de balise'

        tmp = node.find('field[@name="name"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "name"')
        menu.name = tmp.text

        tmp = node.find('field[@name="icon"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "icon"')
        menu.icon = tmp.text

        tmp = node.find('field[@name="sequence"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "sequence"')
        menu.sequence = eval(tmp.get('eval'))

        tmp = node.find('field[@name="sequence"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "sequence"')
        menu.sequence = eval(tmp.get('eval'))

        tmp = node.find('field[@name="view_id"]')
        if tmp is None:
            raise ValueError(f'{err_msg} "view_id"')
        menu.main_view = menu.get_ref(tmp)

        tmp = node.find('field[@name="is_always_new"]')
        if tmp is None:
            menu.no_cache = cls.no_cache
        else:
            menu.no_cache = bool(eval(tmp.get('eval', 'False')))

        tmp = node.find('field[@name="is_deprecated"]')
        if tmp is None:
            menu.deprecated = cls.deprecated
        else:
            menu.deprecated = bool(eval(tmp.get('eval', 'False')))

        tmp = node.find('field[@name="parent_id"]')
        if tmp is None:
            menu.parent = cls.parent
        else:
            menu.parent = menu.get_ref(tmp)

        tmp = node.find('field[@name="help"]')
        if tmp is None:
            menu.help = cls.help
        else:
            menu.help = tmp.text

        tmp = node.find('field[@name="initial_onchange_id"]')
        if tmp is None:
            menu.init_oc = cls.init_oc
        else:
            menu.init_oc = menu.get_ref(tmp)

        tmp = node.find('field[@name="view_ids"]')
        if tmp is None:
            menu.views = []
        else:
            intermediate = tmp.get('eval', '')
            menu.views = record.parse_refs(intermediate)

        tmp = node.find('field[@name="css_ids"]')
        if tmp is None:
            menu.styles = []
        else:
            intermediate = tmp.get('eval', '')
            menu.styles = record.parse_refs(intermediate)

        tmp = node.find('field[@name="onchange_ids"]')
        if tmp is None:
            menu.onchanges = []
        else:
            intermediate = tmp.get('eval', '')
            menu.onchanges = record.parse_refs(intermediate)

        return menu

    def to_xml(self) -> str:
        """Transforms the record into a string of its XML serialization, omitting
        superfluous values
        """
        return '\n'.join(filter(lambda x: x is not None, [
            f"""    <record id="{self.xml_id}" model="ir.ui.menu.ionic">""",
            f"""        <field name="name">{self.name}</field>""",
            f"""        <field name="parent_id" ref="{self.parent}"/>""" if self.parent is not None else None,
            f"""        <field name="is_deprecated" eval="{self.deprecated}"/>""" if self.deprecated is not None else None,
            f"""        <field name="is_always_new" eval="{self.no_cache}"/>""" if self.no_cache is not None else None,
            f"""        <field name="icon" type="char">{self.icon}</field>""",
            f"""        <field name="sequence" eval="{self.seq}"/>""",
            f"""        <field name="view_id" ref="{self.main_view}"/>""",
            f"""        <field name="initial_onchange_id" ref="{self.init_oc}"/>""",
            f"""        <field name="view_ids" eval="[(6, 0, [{record.make_refs(self.views)}])]"/>""" if self.views else None,
            f"""        <field name="css_ids" eval="[(6, 0, [{record.make_refs(self.styles)}])]"/>""" if self.styles else None,
            f"""        <field name="onchange_ids" eval="[(6, 0, [{record.make_refs(self.onchanges)}])]"/>""" if self.onchanges else None,
            f"""        <field name="help">{self.help}</field>""" if self.help is not None else None,
            f"""    </record>""",
            f"""""",
        ]))
