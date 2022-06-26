import PySimpleGUI as sg
from main import *


def Menu():

  # Retrieve a list of file types based on the modules.
  # '__modules__' is a dict of all modules' names and objects
  # Refer to 'modules/__init__.py' for relevant code. 
  file_types_list = [] 
  for extension in modules.__modules__.keys():
    extension = '*.' + extension
    file_type_part = ('Model', extension)
    file_types_list.append(file_type_part)


  # While defining the menu seems like a mess of a code, there's no better way (?)
  column1 = [
              [sg.Text('Welcome to Kozmadeus!', size=(24,1), 
                        justification='c', font=('Helvetica', 15))],
              [sg.Text('Select a model to process:')], 
              [sg.InputText(size=(29,1)), 
                sg.FilesBrowse(file_types=file_types_list)],
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

  window = sg.Window(f'Kozmadeus {version_number}', layout, 
                      element_justification='c', resizable=True).Finalize()
      

  while True:
    try:
          
      event, values = window.Read()
      if event is None:
        break

      elif event == 'Submit':
        file_names = values[0]
        window['_done_'].Update('')
              
        if window['_articulated-mode_'].Get() == True:
          template = 'template_articulated'
        elif window['_static-mode_'].Get() == True:
          template = 'template_static'

        else:

          if file_names != '':
            Main(file_names, template, True)
          else:
            raise Exception('Please select a file!')

      elif event == 'Clear Console':
              window['_output_'].Update('')
              
    except Exception as exception:
      print(exception, window)
      print(separator)


if __name__ == '__main__':
  Menu()