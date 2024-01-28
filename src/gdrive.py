import gspread

_pupil_map = {}
_data_map = {}
_batch_updates = {}
spreadsheet = None


def open_spreadsheet(name, pupil_first_line=5):
    global _pupil_map
    global _data_map
    global spreadsheet

    gc = gspread.oauth()
    spreadsheet = gc.open(name)

    for worksheet in spreadsheet.worksheets():
        data = worksheet.get_all_values()

        # map pupils
        _pupil_map[worksheet.title] = {}
        for line in range(pupil_first_line - 1, len(data)):
            firstname = data[line][1]
            lastname = data[line][0]
            pupil_key = f'{lastname}_{firstname}'
            _pupil_map[worksheet.title][pupil_key] = line + 1

        # map data
        _data_map[worksheet.title] = {}
        for column in range(len(data[0])):
            data_key = data[0][column]
            _data_map[worksheet.title][data_key] = column + 1


def update_cell(section, pupil, data, value):
    global _pupil_map
    global _data_map
    global _batch_updates
    global spreadsheet

    if section not in _pupil_map or pupil not in _pupil_map[section]:
        return False

    if section not in _data_map or data not in _data_map[section]:
        return False

    if section not in _batch_updates:
        _batch_updates[section] = []

    row = _pupil_map[section][pupil]
    col = _data_map[section][data]
    range = f'R{row}C{col}'

    _batch_updates[section].append({
        'range': range,
        'values': [[value]]
    })


def commit():
    global _batch_updates
    global spreadsheet

    for section, updates in _batch_updates.items():
        worksheet = spreadsheet.worksheet(section)
        worksheet.batch_update(updates)
