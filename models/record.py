from abc import abstractmethod
import ast
import re
from functools import reduce
from types import NoneType
from typing import Any, Callable, Optional # Can't use self because python 3.10 🥲

PREFIX_RE = re.compile(r'^([A-Z_]+)_')
REF_RE = re.compile(r'ref\( *\'(.*?)\' *\)')

def parse_refs(expr: str) -> list[str]:
    """Retrieves the name of the references by parsing the expression.
    Had I not been a golem, I'd have created a local ``ref`` identity function.
    Oh well, too late, AST unraveling keeps you sharp I guess
    """
    tree = ast.parse(expr)
    names = []
    if not tree.body:
        return names

    root = tree.body[0]
    if not isinstance(root, ast.Expr):
        return names
    elif not isinstance(root.value, (ast.List, ast.Tuple)):
        return names

    for sub_expr in root.value.elts:
        command = sub_expr.elts[0].value
        match command:
            case 4:
                if not isinstance(sub_expr.elts[1], ast.Call) or sub_expr.elts[1].func.id != 'ref':
                    continue
                names.append(sub_expr.elts[1].args[0].value)
            case 6:
                for call in sub_expr.elts[2].elts:
                    if not isinstance(call, ast.Call) or call.func.id != 'ref':
                        continue
                    names.append(call.args[0].value)

    return names


def sanitize(text: str, reverse: bool = False, light: bool = False) -> str:
    """(un/)Sanitizes text for xml

    :param text: The string to sanitize
    :param reverse: Unsanitize instead
    :param light: Only take chevrons into account
    :return: Transformed string
    """
    SANITY_TABLE = [
        ('<', '&lt;'),
        ('>', '&gt;'),
    ]
    if not light:
        SANITY_TABLE.extend([
            ('&', '&amp;'), ('"', '&quot;'), ("'", '&apos;')
        ])
    first, sec = (0, 1) if not reverse else (1, 0)
    # Successively calls replace() on the value with the content of the table
    sanitized_value = reduce(lambda val, repl: val.replace(repl[first], repl[sec]), SANITY_TABLE, text)
    return sanitized_value


def make_refs(xml_ids: list) -> str:
    """Structures a list of xml_ids into calls of ref() for eval

    :param xml_ids: list of xml ids to call ref() on
    :return: string of all the formatted refs, ready to be put into a data file
    """
    xml_ids = list(filter(None, xml_ids))
    if(not xml_ids):
        return ''
    refs = '\n'.join([f"{' ' * 12}ref('{name}')," for name in xml_ids])
    return f"\n{refs}\n{' '*8}"


class Record:
    quirky: Optional[bool] = None # Flag for records whose id does not conform to the convention
    _ext: str # File extension associated with record type
    _code_attr: str # Name of the attribute which holds the record's code

    def __init(self):
        self._ext = None
        self._code_attr = None

    def __remove_prefix(self, prefix: str, prefixed_fields: list[str] = []):
        """Removes the prefix from the fields that have it.
        If the prefix is not found in the record's ID, flag the record as
        quirky

        :param prefix: Prefix
        :param prefixed_fields: Fields (other than xml_id) to strip the prefix from
        """
        if prefix not in self.xml_id:
            self.quirky = True
            return

        self.xml_id = self.xml_id.replace(f"{prefix}_", '')

        for field in prefixed_fields:
            val = getattr(self, field)
            setattr(self, field, val.replace(f"{prefix}_", ''))

    def to_dict(self, prefix: str|None, prefixed_fields: list[str] = []) -> dict[str, Any]:
        """Transforms the record into a dictionary, omitting as many values as
        possible.
        All attributes whose values are the class' default are omitted.
        Serializes the record's code into a file
        :param prefix: Prefix of the scenario
        """
        # Get all defaults ATTRIBUTES of the class. Prune methods & stuff
        class_defaults = self.__class__.__dict__.copy()
        # List cast because it's a generator
        for key, val in list(class_defaults.items()):
            key: str
            private = key.startswith('_')
            callable = isinstance(val, (Callable, classmethod))
            if private or callable:
                del class_defaults[key]

        if prefix is not None:
            self.__remove_prefix(prefix, prefixed_fields)
        self.__separate_code()
        vals = {'id': None} # Key-orderding trick. Nicer yaml output
        vals.update(self.__dict__.copy())
        for key, class_val in class_defaults.items():
            # Can have a slightly different name from what's expected,
            # especially fields tagged as quirky
            if vals.get(key, 'NONE') == class_val:
                del vals[key]

        for key in list(vals.keys()):
            if key.startswith('_'):
                del vals[key]

        # Shorter name
        vals['id'] = vals['xml_id']
        del vals['xml_id']

        return vals

    def __separate_code(self) -> None:
        """Outputs the record's code into a file and removes the 
        corresponding attribute
        """
        if not getattr(self, '_ext', None):
            return

        with open(f"{self.xml_id}.{self._ext}", 'w') as file:
            _ = file.write(getattr(self, self._code_attr).strip())
        delattr(self, self._code_attr)

    def _incorporate_code(self, id: str) -> None:
        """Fetches the records code from its file and sets the correspoding
        attribute
        :param id: shortened id of the record. Must be given since the xml_id
            contains the prefix, while the file does not
        """
        if not getattr(self, '_ext', None):
            return

        with open(f"{id}.{self._ext}", 'r') as file:
            setattr(self, self._code_attr, file.read().strip())

    @classmethod
    @abstractmethod
    def from_dict(cls, dict_: dict[str, Any]) -> "Record":
        """Reconstructs a record from a dictionary, guessing as many values as
        possible"""

    @classmethod
    @abstractmethod 
    def from_xml(cls, node: Any) -> "Record":
        """Reconstructs a record from an xml node, guessing as many values as
        possible"""
        pass

    @abstractmethod
    def to_xml(self) -> str:
        """Transforms the record into a string of its XML serialization, omitting
        superfluous values
        """
        pass

    @staticmethod
    def get_ref(node: Any) -> str:
        """Extracts a ref from a node, handles the case where the ref is gotten
        form an eval call

        :param node: Node to process
        :return: Reference
        :raises ValueError: There is no ref to get (xml is most likely bricked)
        """
        ref = node.get('ref')
        if ref:
            return ref

        eval_ = node.get('eval')
        if not eval_:
            raise ValueError('Node has no ref to extract')

        ref = REF_RE.findall(eval_)
        if not ref:
            raise ValueError('Node has no ref to extract')

        return ref[0]
