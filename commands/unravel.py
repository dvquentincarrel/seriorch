"""Extracts the components of a data file"""

import os
import subprocess
from typing import TypeAlias
# TODO: figure out why on earth this is fine. but `from .. import models` is wrong
import models
from commands.init import init
from lxml import etree


def unravel(data_file: str, config: dict) -> None:
    """Takes a data file and decomposes it.
    - Initializes the project if not done before
    - creates the files
    - populates the skeleton
    - updates the destination location

    :param data_file: File to decompose
    :param confing: Global config. Used to test for auto-commit on unraveling
    """
    records: dict[str, list[models.Record]]
    # Also creates records files
    records = {key:list(val.values()) for key, val in _parse_file(data_file).items()}

    if not os.path.exists('skeleton.yaml'):
        init(config)

    models.utils.make_skeleton(
        config,
        'skeleton.yaml',
        records['onchange'],
        records['view'],
        records['style'],
        records['label'],
        records['param'],
        records['menu'][0],
    )

    # Update destination symlink, we *do* want to discard the previous one
    destination = os.path.dirname(data_file)
    try:
        os.remove('location')
    except:
        pass
    os.symlink(destination, 'location')

    if config['unravel_commit']:
        subprocess.run('git add .; git commit --no-verify -m "Unravel"', shell=True)


Record: TypeAlias = models.Onchange | models.View | models.Style | models.Label | models.Param | models.Scenario
def _parse_file(path: str) -> dict[str, dict[str, Record]]:
    """Parses the given file and extracts the models inside"""

    # Remove newlines between tags, replace all other with something else to circumvent
    # the xml specification's most bright idea of removing any and all newline it can
    # possibly find anywhere within the definition of a tag
    with open(path, 'r') as file:
        content = file.read().strip()
        ## This WILL be an issue someday
        #content = re.sub('>[ \n]*<', '><', content)
        #content = content.replace('\n', '&#182;')
    root = etree.fromstring(bytes(content, 'utf-8'))

    onchanges = root.xpath('//record[@model="manual.onchange"]')
    views = root.xpath('//record[@model="ir.ui.view.ionic"]')
    labels = root.xpath('//record[@model="ir.ui.menu.ionic.label"]')
    params = root.xpath('//record[@model="ir.ui.menu.ionic.param"]')
    scenarios = root.xpath('//record[@model="ir.ui.menu.ionic"]')
    css_pages = root.xpath('//record[@model="ir.ui.css.ionic"]')

    oc_dict = {}
    for onchange in onchanges:
        _ = models.Onchange.from_xml(onchange)
        oc_dict[_.xml_id] = _

    views_dict = {}
    for view in views:
        _ = models.View.from_xml(view, path)
        views_dict[_.xml_id] = _

    labels_dict = {}
    for label in labels:
        _ = models.Label.from_xml(label)
        labels_dict[_.xml_id] = _

    params_dict = {}
    for param in params:
        _ = models.Param.from_xml(param)
        params_dict[_.xml_id] = _

    css_pages_dict = {}
    for css_page in css_pages:
        _ = models.Style.from_xml(css_page)
        css_pages_dict[_.xml_id] = _

    menus_dict = {}
    for scenario in scenarios:
        _ = models.Scenario.from_xml(scenario)
        menus_dict[_.xml_id] = _

    return {
        'onchange': oc_dict,
        'view': views_dict,
        'label': labels_dict,
        'param': params_dict,
        'style': css_pages_dict,
        'menu': menus_dict,
    }
