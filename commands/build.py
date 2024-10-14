"""Builds an xml data file"""

from models import utils
import shutil

def build(config: dict) -> None:
    """Create the final xml file, move or copy it to the destination"""
    data_template = '\n'.join([
        '<?xml version="1.0" encoding="utf-8"?>',
        f"<{config['surrounding_tag']}>",
        "<data>",
        "{}",
        "</data>",
        f"</{config['surrounding_tag']}>",
    ])
    scen, onchanges, views, styles, labels, params = utils.rebuild_models('skeleton.yaml')
    make_xml = lambda x: [y.to_xml() for y in x]
    make_xml_opt = lambda x, y: [z.to_xml(y) for z in x]
    record_xml = '\n'.join([
        *make_xml(onchanges),
        *make_xml(views),
        *make_xml(styles),
        scen.to_xml(),
        *make_xml_opt(labels, scen.xml_id),
        *make_xml_opt(params, scen.xml_id),
    ])

    with open(config['build_name'], 'w') as file:
        file.write(data_template.format(record_xml))

    if config['keep_build']:
        callback = shutil.copy2
    else:
        callback = shutil.move
    callback(config['build_name'], f'location/data_{scen.xml_id}.xml')
