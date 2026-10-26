"""Small explicit interpreter for the shipped contract's supported JSON Schema subset."""
import re
from pathlib import Path
from .core import MigrationError, read_json

SCHEMA = read_json(Path(__file__).resolve().parents[2] / 'schemas/ios-harness-v2.schema.json')


def validate(value, name):
    def walk(value, rule, path):
        if '$ref' in rule:
            walk(value, SCHEMA['$defs'][rule['$ref'].split('/')[-1]], path)
        kind = rule.get('type')
        valid = {'object': lambda: isinstance(value, dict), 'array': lambda: isinstance(value, list),
                 'string': lambda: isinstance(value, str), 'integer': lambda: type(value) is int,
                 'boolean': lambda: type(value) is bool, 'null': lambda: value is None,
                 'number': lambda: type(value) in {int, float}}
        if kind and (kind not in valid or not valid[kind]()):
            raise MigrationError(path + ': expected ' + kind)
        if 'const' in rule and (type(value) is not type(rule['const']) or value != rule['const']):
            raise MigrationError(path + ': invalid constant')
        if 'enum' in rule and not any(type(value) is type(item) and value == item for item in rule['enum']):
            raise MigrationError(path + ': invalid enumeration')
        if isinstance(value, str):
            if len(value.strip()) < rule.get('minLength', 0) or 'pattern' in rule and not re.search(rule['pattern'], value):
                raise MigrationError(path + ': invalid string')
        if type(value) is int and not rule.get('minimum', value) <= value <= rule.get('maximum', value):
            raise MigrationError(path + ': integer outside bounds')
        if isinstance(value, list):
            if len(value) < rule.get('minItems', 0):
                raise MigrationError(path + ': too few items')
            if rule.get('uniqueItems') and any(value[i] in value[:i] for i in range(len(value))):
                raise MigrationError(path + ': duplicate array items')
            if 'items' in rule:
                for i, item in enumerate(value): walk(item, rule['items'], f'{path}[{i}]')
        if isinstance(value, dict):
            if set(rule.get('required', [])) - value.keys():
                raise MigrationError(path + ': missing required fields ' + ','.join(sorted(set(rule['required']) - value.keys())))
            for key, item in value.items():
                if key not in rule.get('properties', {}) and rule.get('additionalProperties') is False:
                    raise MigrationError(path + ': unknown field ' + key)
                child = rule.get('properties', {}).get(key, rule.get('additionalProperties'))
                if isinstance(child, dict): walk(item, child, path + '.' + key)
    walk(value, SCHEMA['$defs'][name], name)
    return value
