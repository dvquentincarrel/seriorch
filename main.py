#!/bin/env python
import os
import yaml
import shutil
import args

class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

try:
    real_path = os.readlink(__file__)
except OSError:
    real_path = __file__

project_dir = os.path.dirname(real_path)

def ensure_config_exists() -> str:
    """Makes sure config is setup and returns its path"""
    config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.local/config'))
    if not os.path.exists(f"{config_dir}/seriorch"):
        os.makedirs(f"{config_dir}/seriorch")
    if not os.path.exists(f"{config_dir}/seriorch/config.yaml"):
        shutil.copy2(f"{project_dir}/data/config.yaml", f"{config_dir}/seriorch/config.yaml")

    return f"{config_dir}/seriorch/config.yaml"

config = {
    'config_file': ensure_config_exists(),
    'yaml_dump': lambda content, file: yaml.dump(content, file, sort_keys=False, Dumper=IndentDumper),
}

with open(f"{project_dir}/data/skeleton_template.yaml", 'r') as file:
    config['skeleton_template'] = yaml.full_load(file)

with open(config['config_file'], 'r') as file:
    config.update(yaml.full_load(file))

# Allows project-specific config items to be defined in the skeleton
if os.path.exists('skeleton.yaml'):
    with open('skeleton.yaml', 'r') as file:
        skeleton_content = yaml.full_load(file)
        if 'config' in skeleton_content:
            config.update(skeleton_content['config'])

args.parse_args(config)
