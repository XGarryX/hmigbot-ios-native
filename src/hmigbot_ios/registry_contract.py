"""Read every canonical placeholder group without guessing column identities."""
import re
from .artifact_contract import _cells, _visible_lines, markdown_tables
from .core import MigrationError

HEADERS = ['P-ID', 'location', 'trigger_condition', 'status', 'kind', 'resolve_by']
ID_PATTERN = r'P-[A-Za-z0-9._-]+'


def parse(text):
    tables, rows, row_lines = [], {}, set()
    for table in markdown_tables(text):
        if 'P-ID' not in table['headers']:
            continue
        if table['headers'] != HEADERS:
            raise MigrationError('Registry group at line '+str(table['line'])+
                                 ' requires canonical column order: '+', '.join(HEADERS))
        tables.append(table)
        for line, cells in zip(table['row_lines'], table['rows']):
            if (len(cells) != len(HEADERS) or any(not cell for cell in cells)
                    or not re.fullmatch(ID_PATTERN, cells[0]) or cells[0] == 'P-ID'
                    or cells[0] in rows):
                raise MigrationError('Invalid, incomplete or duplicate registry ID at line '+str(line))
            rows[cells[0]] = dict(zip(HEADERS, cells))
            row_lines.add(line)
    if not tables:
        raise MigrationError('Registry requires a complete canonical six-column table')
    for line, value in _visible_lines(text):
        cells = _cells(value)
        if cells and cells[0].startswith('P-') and cells[0] != 'P-ID' and line not in row_lines:
            raise MigrationError('Registry row outside a canonical table at line '+str(line)+
                                 '; use explicit ensure_table_headers repair before writeback')
    structure = '\n'.join(line for number, line in enumerate(text.splitlines(), 1) if number not in row_lines)
    return structure, rows
