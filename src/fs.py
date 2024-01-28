from pathlib import Path


def get_dirs(path):
    dirs = []

    for item in sorted(Path(path).glob('*')):
        if item.is_dir() and item.name[0] != '.':
            dirs.append(item)

    return dirs


def get_pupil_dirs(path):
    """
    - the first level of the directory hierarchy contains folders for each class section
    - the second level of the directory hierarchy contains the individual work folders of each pupil
    :param path:
    :return:
    """
    pupil_dirs = []

    for item in get_dirs(path):
        if item.name[0:3] != 'SEC':
            continue

        section_dir = item
        for pupil_dir in get_dirs(section_dir):
            pupil_dirs.append((section_dir.name, pupil_dir))

    return pupil_dirs
