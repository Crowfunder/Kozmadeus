from webbrowser import open as OpenURL
import PySimpleGUI as sg
from main import *

# Define a few constants
url_twitter = 'https://twitter.com/crowfunder'
url_github  = 'https://github.com/Crowfunder/Kozmadeus'
url_manual  = 'https://github.com/Crowfunder/Kozmadeus/wiki'
url_bugs    = 'https://github.com/Crowfunder/Kozmadeus/discussions/categories/bugs-issues'

def WindowAbout():
  
  layout_credits = [
                      [
                        sg.Text('Credits:', size=(16,1))
                      ],
                      [
                        sg.Push(),
                        sg.Text('- Puzovoz (Author of Bootshuze)\n'
                                '- XanTheDragon (Substantive Support)\n'
                                '- Kirbeh (Current Logo)\n'
                                '- Whoever gave Kozma her name\n '
                                '(Enabled me to make that joke)',
                                font=('Helvetica', 11)),
                        sg.Push()
                      ],

                   ]
  
  layout_about = [
                   [
                      sg.Text('About', size=(24,1), 
                              justification='c', font=('Helvetica', 15))
                   ],
                   [
                      sg.Push(),
                      sg.Text('Script written with love, by Crowfunder',
                              font=('Helvetica', 11)),
                      sg.Push(),
                      sg.VPush()
                   ]
                 ]
  
  layout = [
              [
                sg.Frame(title='', layout=layout_about)
              ],
              [
                sg.Frame(title='', layout=layout_credits)
              ],
              [
                sg.Button('Kozmadeus\n Github', size=(16,2), key='_URL-GITHUB_'),
                sg.Push(),
                sg.Button('Follow me\n on Twitter', size=(16,2), key='_URL-TWITTER_')
              ]
           ]
  
  window_about = sg.Window('About', layout, element_justification='c',
                           finalize=True)
  window_about.bind('<Escape>', 'Exit')
  
  # Bring window to front
  window_about.bring_to_front()
  
  while True:
    event, values = window_about.Read()
    
    if event is None or event == 'Exit':
      window_about.close()
      break
    
    elif event == '_URL-GITHUB_':
      OpenURL(url_github)
    
    elif event == '_URL-TWITTER_':
      OpenURL(url_twitter)

def Menu():

  # Define the shortcut menubar buttons as strings
  # to shorten the events-related code
  menubar_open    = 'Open              Ctrl-O'
  menubar_clear_q = 'Clear Queue    Ctrl-Q'
  menubar_clear_c = 'Clear Console   Ctrl-R'
  
  # Predefining file_names as empty list 
  # Necessary to make Listbox work
  file_names = []
  
  # Set the PySimpleGUI Theme
  sg.theme('DarkGrey')
  
  # Define all UI components
  menubar = [
              [
                '&File', 
                  [
                    f'&{menubar_open}', 
                    f'&{menubar_clear_q}'
                  ]  
              ],
              [
                '&Edit', 
                  [
                    f'&{menubar_clear_c}'
                  ]
              ],
              [
                '&Options', 
                  [
                    '&Modules',
                    '&Restore Files',
                    '&Check for Updates'
                  ]
              ],
              [
                '&Help',
                  [
                    '&About',
                    '&Manual',
                    '&Report a bug'
                  ]  
              ]
            ]
  
  frame_output_type = [
                        [
                          sg.Radio('Articulated','OUTPUT_TYPE', default=True,
                                    tooltip='Output model as Articulated type',
                                    key='_ARTICULATED-MODE_'),
                          sg.Radio('Static', 'OUTPUT_TYPE', key='_STATIC-MODE_', 
                                   tooltip='Output model as Static type'),
                          sg.Radio('Animations\nOnly', 'OUTPUT_TYPE', key='_ANIMATION-MODE_', 
                                   tooltip='Output just the model animations (if they exist)',
                                   visible=False)
                        ]
                      ]

  frame_files_list = [
                        [
                          sg.Listbox(size=(30,10), horizontal_scroll=True, 
                                     values=[], key='_FILES_', enable_events=True, 
                                     tooltip='Click on model to remove it from list', 
                                     expand_x=True)
                        ]
                     ]
  
  column_left = [
                  [
                    sg.Text('Welcome to Kozmadeus!', size=(24,1), 
                            justification='c', font=('Helvetica', 15))
                  ],
                  [
                    sg.Text('Select models to process'), 
                    sg.Input(key='_FILEBROWSE_', enable_events=True, visible=False),
                    sg.FilesBrowse(file_types=file_types_list, target='_FILEBROWSE_', size=[10,1]),
                  ],
                  [
                    sg.Checkbox('Future Option 1', visible=False),
                    sg.Combo(['Opt1', 'Opt2'], readonly=True, visible=False, default_value='Opt1')
                  ],
                  [
                    sg.Frame(layout=frame_output_type, title='Output Type', expand_x=True)
                  ],
                  [
                    sg.Button('Submit', expand_x=True), 
                  ],
                  [
                    sg.Frame(layout=frame_files_list, title='Selected Files', expand_x=True)  
                  ]
                ]

  column_right = [
                    [
                      sg.Multiline(expand_x=True, expand_y=True, key='_OUTPUT_', 
                                   auto_refresh=True, write_only=True, autoscroll=True, 
                                   reroute_stdout=True, reroute_stderr=True, 
                                   echo_stdout_stderr=True, disabled=True)
                    ],
                    [
                      sg.Button('Clear Console', pad=((5,200),(0,0))),
                      sg.Text('', text_color='lawn green', key='_DONE_', size=(5,1)),
                    ]
                 ]

  layout = [
              [
                sg.Menu(menubar),
                sg.Frame(layout = column_left, title=''), 
                sg.Frame(layout = column_right, title='Console', expand_x=True, expand_y=True)
              ]
           ]

  window = sg.Window(f'Kozmadeus {version_current}', layout, 
                       element_justification='c', finalize=True)
      
  # Define simpler to read shortcut events
  window.bind('<Control-o>', 'Ctrl-O')
  window.bind('<Control-q>', 'Ctrl-Q')
  
  # Connect menubar events with existing ones
  window.bind('<Control-r>', 'Clear Console')
  window.bind('menubar_clear_c', 'Clear Console')
  window.bind('<Return>', 'Submit')
  
  # Bring window to front on start
  window.bring_to_front()

  # Main events and values loop
  while True:
    try:
      
      event, values = window.Read()
      
      # Program exit event
      if event is None:
        break


      # Files Queue related events
      elif event == '_FILEBROWSE_':
        file_names = values['_FILEBROWSE_'].split(';')
        window['_FILES_'].Update(file_names)
        
      elif values['_FILES_']:
        file_names.remove(values['_FILES_'][0])
        window['_FILES_'].Update(file_names)
        
        
      # Menubar shortcut related events
      elif event in (menubar_open   , 'Ctrl-O'):
        file_names = sg.PopupGetFile('file to open', no_window=True,
                                     multiple_files=True,
                                     file_types=file_types_list)
        
        # For some reason, PopupGetFile returns tuple
        # Needs conversion to list
        file_names = list(file_names)
        window['_FILES_'].Update(file_names)
        
      elif event in (menubar_clear_q, 'Ctrl-Q'):
        file_names = []
        window['_FILES_'].Update(file_names)


      # Menubar remaining events
      elif event == 'Modules':
        ModuleData()
        print(separator)

      elif event == 'Restore Files':
        RestoreFiles()
        print(separator)

      elif event == 'Check for Updates':
        CheckUpdates()
        print(separator)

      elif event == 'Manual':
        OpenURL(url_manual)

      elif event == 'About':
        window.disable()
        WindowAbout()
        window.enable()
        window.bring_to_front()
        
      elif event == 'Report a bug':
        OpenURL(url_bugs)


      # Button related events and others
      elif event in (menubar_clear_c, 'Ctrl-R', 'Clear Console'):
        window['_OUTPUT_'].Update('')
      
      elif event == 'Submit':
        window['_DONE_'].Update('')
              
        # Get the user settings
        if window['_ARTICULATED-MODE_'].Get():
          template = 'template_articulated'
        elif window['_STATIC-MODE_'].Get():
          template = 'template_static'

        if file_names:
          Main(file_names, template, False)
          window['_DONE_'].Update('Done!')
          window.ding()
          print(separator)
          
        else:
          raise Exception('Please select a file!')
        
              
    except Exception as exception:
      print(exception)
      print(separator)


if __name__ == '__main__':
  Menu()
