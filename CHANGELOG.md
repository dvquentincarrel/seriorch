# 1.4
- Config can be overridden by the skeleton
- Location symlink is now ignored by git
- Added ruff config
- Watched commands are silent in the background
- Check db key is filled before injection

# 1.3
- Add use of the watch config key / cli flag to automatically rerun build / inject
- Allow injection of labels in v10
- Improve error handling
- Fix typo in CSS injection
- Allow the use of scenarios with initial onchanges

# 1.2
- Enforce better ordering of skeleton keys
- Allow scenarios to be built from skeleton without any initial onchange entry

# 1.1
- Add installation procedure and FAQ in the readme
- The surrounding tag in the data file is configurable
- Allow generation of data files whose name differ from their xml id
- Fix ref name generation for quirky records
- Fix xml serialization of translatable records
- Move around order of fields in xml output to reduce the size of the diff after a build

# 1.0
Everything mostly functional, at long last, unraveling doesn't mess up the xml.
Updating an existing file is still not implemented
