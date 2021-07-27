import PySimpleGUI as sg


def main():

    layout = [[sg.T("")], [sg.Text("Select the CSV file containing your term / phrase lexicons: "),
                           sg.Input(key="-IN2-", change_submits=True), sg.FileBrowse(key="-IN-")],
              [sg.T("")], [sg.Text("Which lexicons (column headers) do you want to include?"),
                           sg.Checkbox("All lexicons    ", key="lexicons_all"),
                           sg.InputText(" Separate column header names with underscores (e.g. Lexicon1_Lexicon2): ",
                                        key="lexicon_text")], [sg.T("")],
              [sg.Checkbox("Would you like to include additional lexicons that need to be explicitly declared "
                       "(ex. HateBase)?", key="include_hatebase")],
              [sg.T("")],
              [sg.Text("Select a folder to save your CSV report outputs: "),
               sg.Input(key="-IN4-", change_submits=True), sg.FolderBrowse(key="-IN3-")],
              [sg.T("")], [sg.Text("If applicable, select the file directory containing your EAD (.xml) files: "),
                           sg.Input(key="-IN6-", change_submits=True), sg.FolderBrowse(key="-IN5-")],
              [sg.T("")], [sg.Text("If applicable, select the MARCXML file containing your MARC records (a single XML "
                                   "file with multiple records): "),
                           sg.Input(key="-IN8-", change_submits=True), sg.FileBrowse(key="-IN7-")], [sg.T("")],
              [sg.Submit()]]

    window = sg.Window('Library Description Audit Setup', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break   # Program exited
        elif event == "Submit":
            print(values)
            lexicon_csv_path = values["-IN2-"]
            if values['include_hatebase']:
                hatebase_include = 1
            else:
                hatebase_include = 0
            if values["lexicons_all"]:
                lexicon_test = 'ALL'
            else:
                lexicon_test = values["lexicon_text"]
            output_path = values['-IN3-']
            if not values["-IN5-"] and not values['-IN6-']:
                ead_path = 'NONE'
            else:
                ead_path = values["-IN5-"]
            if not values["-IN7-"] and not values['-IN8-']:
                marcxml_path = 'NONE'
            else:
                marcxml_path = values["-IN7-"]
            window.close()
            ret = [lexicon_csv_path, lexicon_test, hatebase_include, output_path, ead_path, marcxml_path]
            return ret
            # TODO: Area of expansion for next version--add in visualizations that show breakdown of match location,
            #  type, etc. that are produced and shown in GUI after matching is complete


if __name__ == '__main__':
    main()
