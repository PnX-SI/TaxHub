from pathlib import Path

import toml
from marshmallow import EXCLUDE
from marshmallow.exceptions import ValidationError


class ConfigError(Exception):
    """
    Configuration error class
    Quand un fichier de configuration n'est pas conforme aux attentes
    """

    def __init__(self, file, value):
        self.value = value
        self.file = file

    def __str__(self):
        msg = "Error in the config file '{}'. Fix the following:\n"
        msg = msg.format(self.file)
        for key, errors in self.value.items():
            msg += "\n\t{}:\n\t\t- {}".format(key, errors)
        return msg


def load_and_validate_toml(toml_file, config_schema, partial=None):
    """
    Fonction qui charge un fichier toml
     et le valide avec un Schema marshmallow
    """
    if toml_file:
        toml_config = load_toml(toml_file)
    else:
        toml_config = {}
    try:
        configs_py = config_schema().load(toml_config, unknown=EXCLUDE, partial=partial)
    except ValidationError as e:
        raise ConfigError(toml_file, e.messages)
    return configs_py


def load_toml(toml_file):
    """
    Fonction qui charge un fichier toml
    """
    if not Path(toml_file).is_file():
        raise Exception("Missing file {}".format(toml_file))
    return toml.load(str(toml_file))
