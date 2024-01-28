import gspread

_pupil_map = {}
_data_map = {}


def open(name, pupil_first_line=5):
    gc = gspread.oauth()
    sh = gc.open(name)

    for wks in sh.worksheets():
        line = pupil_first_line

        # col1 =

        while wks.cell(line, 1).value:
            pupil = wks.cell(line, 1).value + '_' + wks.cell(line, 2).value
            print(pupil)
            line += 1




    #gc = gspread.oauth()
    #sh = gc.open("SNT 2023-2024 - Minisites")
    #wks = sh.worksheet('SEC03')
    #print(wks.cell(5, 1).value)