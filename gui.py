import PySimpleGUI as sg
from main import *

""" def console_print(text, window):
  print(text)
  window.Refresh() """

def menu():

  column1 = [
              [sg.Text('Welcome to Kozmadeus!', size=(24,1), 
                        justification='c', font=('Helvetica', 15))],
              [sg.Text('Select a model to process:')], 
              [sg.InputText(size=(29,1)), 
                sg.FileBrowse(file_types=(("Collada Files", "*.dae"),
                                         ("Wavefront Files", "*.obj")))],
              [sg.Radio('Articulated','OUTPUT_TYPE', default=True,
                        tooltip='Output model as Articulated type',
                        key='_articulated-mode_'),
                sg.Radio('Static', 'OUTPUT_TYPE', key='_static-mode_', 
                        tooltip='Output model as Static type')],
              [sg.Button('Submit'), 
                sg.Text('', text_color='lawn green', key='_done_',
                        size=(5,1))]
            ]

  column2 = [
              [sg.Output(size=(36,6), key='_output_')],
              [sg.Button('Clear Console')]
            ]

  layout = [[sg.Frame(layout = column1, title='')], 
            [sg.Frame(layout = column2, title='Console')]]

  window = sg.Window('Kozmadeus v0.0.1', layout, 
                      element_justification='c').Finalize()
      

  while True:
    try:
          
      event, values = window.Read()
      if event is None:
        break

      elif event == 'Submit':
        file = values[0]
        window['_done_'].Update('')
              
        if window['_articulated-mode_'].Get() == True:
          template = "template_articulated"
        elif window['_static-mode_'].Get() == True:
          template = "template_static"

        file_name = os.path.basename(file).replace('.obj', '')
        if os.path.isfile(f'{file_name}.xml'):
          print(f'File {file_name}.xml '
                         'already exists! Halting!')

        else:
          if file != '':
            print(fr'''Processing "{file}"...''')
            #main(file, file_name, window, template)
          else:
            raise Exception('Please select a file!')
          print(separator)

      elif event == 'Clear Console':
              window['_output_'].Update('')
              
    except Exception as e:
      print(e, window)
      print(separator)

if __name__ == '__main__':

  if not os.path.isfile('templates/template_articulated'):
    if not os.path.isfile('templates/template_static'):
      try:

        sg.Popup('Downloading template files...', button_type=5,
                  auto_close=True, no_titlebar=True)
        templates_download()

      except:

        sg.PopupError("Template files are missing, make " 
                      "sure they are in the same directory "
                      "as this script and start again.")  
        quit()

  menu()