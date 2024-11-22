import os
from time import sleep
from typing import Any
from psycopg2.extensions import connection
import yaml
import models
from .onchange import Onchange
from .view import View
from .style import Style
from .label import Label
from .param import Param
from .scenario import Scenario
import psycopg2 as pcg


def reoarder_skeleton(skeleton: dict[str, Any]) -> dict:
    """Creates a skeleton with reordered keys, for ergonomy"""
    first_keys = [
        'db', 'file_name', 'prefix', 'name', 'deprecated', 'icon',
        'sequence', 'main_view', 'quirky_main_view', 'init_oc',
        'quirky_init_oc'
    ]
    last_keys = ['help']
    ordered_skeleton: dict[str, Any] = {}
    for key in first_keys:
        if key in skeleton:
            ordered_skeleton[key] = skeleton[key]
    for val_key in skeleton.keys():
        if val_key not in first_keys + last_keys:
            ordered_skeleton[val_key] = skeleton[val_key]
    for key in last_keys:
        if key in skeleton:
            ordered_skeleton[key] = skeleton[key]

    return ordered_skeleton


def make_skeleton(
    config: dict[str, Any],
    filename: str,
    onchanges: list[models.Onchange],
    views: list[models.View],
    styles: list[models.Style],
    labels: list[models.Label], # pyright: ignore[reportUnusedParameter]
    params: list[models.Param], # pyright: ignore[reportUnusedParameter]
    scenario: models.Scenario,
):
    new_onchanges = [oc.xml_id for oc in onchanges]
    new_views = [view.xml_id for view in views]
    new_styles = [sheet.xml_id for sheet in styles]
    structure = scenario.to_dict(new_onchanges, new_views, new_styles)
    make_dict = lambda rcs: [rc.to_dict(scenario.xml_id) for rc in rcs]
    for rec_type in ['styles', 'onchanges', 'views', 'labels', 'params']:
        structure[rec_type] = make_dict(locals()[rec_type])


    # If the file already exists and has been populated with unguessable data
    # e.g. the db name for injection
    if not os.path.exists(filename):
        existing_vals = {} 
    else:
        with open(filename, 'r') as file:
            existing_vals = yaml.full_load(file)
    existing_vals.update(structure)
    existing_vals = reoarder_skeleton(existing_vals)

    # TODO: Reuse file open for reading by resetting cursor and overwriting
    with open(filename, 'w') as file:
        config['yaml_dump'](existing_vals, file)


def rebuild_models(
    filename: str
) -> tuple[Scenario, list[Onchange], list[View], list[Style], list[Label], list[Param]]:
    """Reconstructs models from skeleton file

    :param filename: Path to skeleton file
    :return: Tuple of the records
    """
    try:
        with open(filename, 'r') as file:
            data = yaml.full_load(file)
    except FileNotFoundError:
        sleep(0.2)
        with open(filename, 'r') as file:
            data = yaml.full_load(file)

    scen = Scenario.from_dict(data)

    recompose = lambda x, data: __recompose(x, data, scen.xml_id)

    onchanges = recompose(Onchange, data.get('onchanges'))
    views = recompose(View, data.get('views'))
    styles = recompose(Style, data.get('styles'))
    labels = recompose(Label, data.get('labels'))
    params = recompose(Param, data.get('params'))

    return (
        scen,
        onchanges,
        views,
        styles,
        labels,
        params,
    )


# def __recompose[T](model: T, data: dict[str, Any], prefix: str) -> list[T]: # Requires python 3.11
def __recompose(model: Any, data: dict[str, Any], prefix: str) -> list[Any]:
    """Recreates a record from its skeleton entry"""
    if not data:
        return []
    func = getattr(model, 'from_dict')
    return [func(datum, prefix) for datum in data]


def get_db_cursor(config: dict[str, Any]) -> pcg.extensions.cursor:
    """Produces the cursor to connect to the configured DB

    :param config: serior configuration
    :return: Cursor to the DB
    """
    # TODO: test
    with open('skeleton.yaml', 'r') as file:
        data = yaml.full_load(file)

    if 'db' not in data:
        raise ValueError("Le squelette n'a pas d'entrée \"db\", qui doit contenir le nom de la bdd.")

    return pcg.connect(database=data['db'], user=config['db_user'], password=config['db_pw'], port=config['db_port']).cursor()
