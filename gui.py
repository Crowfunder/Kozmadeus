###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

# External Imports
from webbrowser import open as OpenURL
import PySimpleGUI as sg
import threading

# Internal Imports
from main import RestoreFiles, CheckUpdates, ModuleData, Main
from main import VERSION_CURRENT, SEPARATOR, FILE_TYPES_LIST


# Define a few constants
URL_DISCORD = 'https://discord.gg/RAf499a'
URL_GITHUB  = 'https://github.com/Crowfunder/Kozmadeus'
URL_MANUAL  = 'https://github.com/Crowfunder/Kozmadeus/wiki'
URL_BUGS    = 'https://github.com/Crowfunder/Kozmadeus/issues'


# noupdate_silent is a flag that disables
# error and "no updates available" popups
def WindowUpdates(noupdate_silent):

  try:
    update_data = CheckUpdates()
    
    if update_data['current'] != update_data['fetched']:
      sg.Popup('Updates available! \nDownload at: '
               'https://github.com/Crowfunder/Kozmadeus/releases\n\n'
              f'Current version: {update_data["current"]}\n'
              f'New version: {update_data["fetched"]}',
              icon='assets/kozmadeus.ico', title='Updates Found',
              font=('Helvetica', 11))

    else:
      if not noupdate_silent:
        sg.Popup('Kozmadeus is up to date!', icon='assets/kozmadeus.ico',
                 title='Up to date', font=('Helvetica', 11))
      

  except Exception as e:
    if not noupdate_silent:
      sg.PopupError('Unable to fetch updates!\n'
                    'Check your internet connection.\n', e,
                    icon='assets/kozmadeus.ico', title='Error',
                    font=('Helvetica', 11))
  
  


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
                      sg.Text('Script written with love, by Crowfunder\n'
                              'Distributed under GPL-3.0 License',
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
                sg.Button('Chat on\n Discord', size=(16,2), key='_URL-DISCORD_')
              ]
           ]
  
  window_about = sg.Window('About', layout, element_justification='c',
                           icon='assets/kozmadeus.ico', finalize=True)
  window_about.bind('<Escape>', 'Exit')
  window_about.bring_to_front()

  while True:
    event, values = window_about.Read()
    
    if event is None or event == 'Exit':
      window_about.close()
      break
    
    elif event == '_URL-GITHUB_':
      OpenURL(URL_GITHUB)
    
    elif event == '_URL-DISCORD_':
      OpenURL(URL_DISCORD)


def GuiMenu():

  # Define the shortcut menubar buttons as strings
  # to shorten the events-related code
  menubar_open    = 'Open              Ctrl-O'
  menubar_clear_q = 'Clear Queue    Ctrl-Q'
  menubar_clear_c = 'Clear Console   Ctrl-R'
  
  # Predefining file_names as empty list 
  # Necessary to make Listbox work
  file_names = list()
  
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
                    '&Report a Bug'
                  ]  
              ]
            ]
  frame_import_opts = [
                        [
                          sg.Checkbox('Strip armature tree data', visible=True, key='_STRIP-ARMATURE-TREE_',
                                      tooltip='Necessary for reimporting armors')
                        ],
                        [
                          sg.Combo(['Opt1', 'Opt2'], readonly=True, visible=False, default_value='Opt1')
                        ]
                      ]
  frame_output_type = [
                        [
                          sg.Radio('Articulated','OUTPUT_TYPE', default=True,
                                    key='_ARTICULATED-MODE_',
                                    tooltip='Output model as Articulated type\n'
                                            'used for most cases'),
                          sg.Radio('Static', 'OUTPUT_TYPE', key='_STATIC-MODE_', 
                                   tooltip='Output model as Static type\n'
                                           'used most notably for importing armors'),
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
                     sg.Image('assets/kozmadeus_full.png', subsample=3)
                  ],
                  [
                    sg.Text('Select models to process'), 
                    sg.Input(key='_FILEBROWSE_', enable_events=True, visible=False),
                    sg.FilesBrowse(file_types=FILE_TYPES_LIST, target='_FILEBROWSE_', size=[10,1]),
                  ],
                  [
                    sg.Frame(layout=frame_import_opts, title='Options', expand_x=True)
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
                      sg.Text('', text_color='lawn green', key='_STATUS_', size=(5,1)),
                    ]
                 ]

  layout = [
              [
                sg.Menu(menubar),
                sg.Frame(layout = column_left, title=''), 
                sg.Frame(layout = column_right, title='Console', expand_x=True, expand_y=True)
              ]
           ]

  window = sg.Window(f'Kozmadeus {VERSION_CURRENT}', layout, 
                       element_justification='c', icon='assets/kozmadeus.ico', finalize=True)
      
  # Define simpler to read shortcut events
  window.bind('<Control-o>', 'Ctrl-O')
  window.bind('<Control-q>', 'Ctrl-Q')
  
  # Connect menubar events with existing ones
  window.bind('<Control-r>', 'Clear Console')
  window.bind('menubar_clear_c', 'Clear Console')
  window.bind('<Return>', 'Submit')
  
  # Bring window to front on start
  window.bring_to_front()

  # Create an Exception Hook for threads
  def ThreadExceptHook(data):
    nonlocal window
    window.write_event_value('_THREAD-ERROR_', data.exc_value)
  threading.excepthook = ThreadExceptHook

  # Lock certain options when processing files to prevent 
  # absolute buffons from breaking the script
  processing_lock = False

  # Refresh the buttons and locks 
  # when the loop cycle is done
  def RefreshWindowButtons():
    nonlocal window
    nonlocal processing_lock
    window['Submit'].Update(disabled=False)
    window.bind('<Return>', 'Submit')
    processing_lock = False
    window.ding()
    
  # Check for updates with noupdate_silent flag
  WindowUpdates(True)

  # Main events and values loop
  while True:
    try:

      event, values = window.Read()
      window.refresh()
      
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
                                     file_types=FILE_TYPES_LIST)
        
        # For some reason, PopupGetFile returns tuple
        # Needs conversion to list
        file_names = list(file_names)
        window['_FILES_'].Update(file_names)
        
      elif event in (menubar_clear_q, 'Ctrl-Q'):
        file_names = []
        window['_FILES_'].Update(file_names)


      # Menubar remaining events
      elif event == 'Modules':
        if not processing_lock:
          processing_lock = True
          ModuleData()
          processing_lock = False
          print(SEPARATOR)

      elif event == 'Restore Files':
        if not processing_lock:
          processing_lock = True
          print('Restoring template files...')
          RestoreFiles()
          print('Success!')
          print(SEPARATOR)

      elif event == 'Check for Updates':
        WindowUpdates(False)

      elif event == 'Manual':
        OpenURL(URL_MANUAL)

      elif event == 'About':
        window.disable()
        WindowAbout()
        window.enable()
        window.bring_to_front()
        
      elif event == 'Report a Bug':
        OpenURL(URL_BUGS)

      
      # Thread Events
      elif event == '_THREAD-ERROR_':
        raise Exception(values['_THREAD-ERROR_'])
      
      elif event == '_THREAD-COMPLETE_':
        window['_STATUS_'].Update('Done!')
        window['_STATUS_'].Update(text_color='lawn green')
        RefreshWindowButtons()


      # Button related events and others
      elif event in (menubar_clear_c, 'Ctrl-R', 'Clear Console'):
        window['_OUTPUT_'].Update('')

      ### BEGIN SUBMIT
      elif event == 'Submit':
        window['_STATUS_'].Update('')
              
        # Get the user settings
        if window['_ARTICULATED-MODE_'].Get():
          template = 'template_articulated'
        elif window['_STATIC-MODE_'].Get():
          template = 'template_static'
        
        strip_armature_tree = window['_STRIP-ARMATURE-TREE_'].Get()

        # Start processing the files
        if file_names:
          
          # Lock the "Submit" button and certain functions
          window['Submit'].Update(disabled=True)
          window.bind('<Return>', 'null')
          processing_lock = True

          # Long boi taken directly from PySimpleGUI Cookbook
          # Creates a separate thread to prevent the program from freezing
          window.start_thread(lambda: Main(file_names, template, 
                                           False, strip_armature_tree), 
                              '_THREAD-COMPLETE_')

        else:
          print('Please select a file!')
      ### END SUBMIT  

    except Exception as exception:
      window['_STATUS_'].Update('Error!')
      window['_STATUS_'].Update(text_color='red')

      print('Unhandled exception has occured:\n', exception)
      print(SEPARATOR)
      RefreshWindowButtons()


if __name__ == '__main__':
  GuiMenu()
