import gdrive

gdrive.open_spreadsheet("SNT 2023-2024 - Minisites")

for pupil in gdrive._pupil_map['SEC07'].keys():
    gdrive.update_cell("SEC07", pupil, "LIV_1", 1)
gdrive.commit()
