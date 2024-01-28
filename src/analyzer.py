import csv
import io
import locale
import unicodedata

import fs
import gdrive


class Context:
    def __init__(self):
        self.section = None
        self.pupil_dir = None
        self.project_name = None
        self.project_dir = None
        self._properties = {}

        self.html_files = []
        self.css_files = []

    def set_property(self, name, value):
        self._properties[name] = value

    def get_property(self, name):
        return self._properties[name]

    def __str__(self):
        return f'{self.section} - {self.pupil_dir.name} - {self.project_name}'


class Report:
    def __init__(self, name):
        self.name = unicodedata.normalize('NFC', name)
        self._data = []

    def append(self, value):
        self._data.append(value)

    def __str__(self):
        str_io = io.StringIO()
        writer = csv.writer(str_io)
        writer.writerow(self._data)

        output = str_io.getvalue().rstrip()
        str_io.close()

        return output


class Runner:
    def __init__(self):
        self._tasks = []
        self._reports = []

    def add_task(self, task, tag=None):
        self._tasks.append((tag, task))

    def run(self, path):
        context = Context()
        context.section, context.pupil_dir = path

        dirs = fs.get_dirs(context.pupil_dir)
        if len(dirs) == 1:
            context.project_dir = dirs[0]
            context.project_name = context.project_dir.name.lower()
        else:
            context.project_dir = context.pupil_dir

        report = Report(context.section + ' - ' + context.pupil_dir.name)
        pupil = unicodedata.normalize('NFC', context.pupil_dir.name)
        self._reports.append(report)

        for tag, task in self._tasks:
            result = task.run(context, report)
            if tag and result:
                gdrive.update_cell(context.section, pupil, tag, result)

    def report(self):
        width = max([len(report.name) for report in self._reports])
        for report in self._reports:
            name = (report.name + ' ').ljust(width + 2, ".")
            print(f'{name} {report}')


class Task:
    def __init__(self):
        pass

    def run(self, context, report):
        raise NotImplementedError


def format_float(n):
    locale.setlocale(locale.LC_NUMERIC, 'fr_FR')
    return locale.format_string("%f", n)
