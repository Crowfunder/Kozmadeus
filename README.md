![banner](https://media.discordapp.net/attachments/955809154105217124/1087392414253203547/Kozmadeus_full_logo.png)

Modular 3D model importer for Spiral Knights ([Clyde](https://github.com/threerings/clyde)). A direct successor of [Bootshuze](https://github.com/Puzovoz/Bootshuze) and [Bootshuze-GUI](https://github.com/Crowfunder/Bootshuze-GUI) completely revamping the design and codebase, as well as adding numerous QOL improvements along with new options. 

It relies on .xml templates that can be imported within Tudey scene viewer ([SpiralView](https://github.com/lucasluqui/spiralview)). 

# Features
- Importing Model Data: Geometries, Texture Mappings, Armatures, ~~Animations~~ (WIP)
- Graphical and Command Line user interfaces
- Importing to either Articulated or Static Spiral Knights XML model template
- Support for various model formats: Collada (.dae), Wavefront (.obj) 
- Importing multiple files at the same time
- Update checker
- Restoring template files, in case they are missing
- Hotkeys (GUI)
- Returning geometry data to stdout (CLI)

# Limitations
- Texture and material data have to be edited manually within SpiralView
- Any imported model edits, such as transformations or scaling have to be done externally, either in model editing software such as [Blender](https://www.blender.org/) (before importing) or in SpiralView, using i.e. compound models (after importing)
- Kozmadeus cannot compile .xml to .dat

For module-specific limitations see [Limitations and Known Issues](https://github.com/Crowfunder/Kozmadeus/wiki/Modules#limitations-and-known-issues)

# Getting Started
For usage instructions, see [Usage](https://github.com/Crowfunder/Kozmadeus/wiki/Usage).
For precise documentation on User Interfaces functionality, see [Bundled User Interfaces](https://github.com/Crowfunder/Kozmadeus/wiki/User-Interfaces#bundled-user-interfaces).
## Precompiled builds
 1. Download the [latest release](https://github.com/Crowfunder/Kozmadeus/releases/latest).
 2. Unzip it.
 3. Run the appropriate executable.
 
 
 ## From source
 1. Install [Python3](https://www.python.org/downloads/) (Python 3.10 is the one that is sure to be working)
 2. Download the [source code of the repo](http.s://github.com/Crowfunder/Kozmadeus/archive/refs/heads/main.zip), unzip it
 3. Open command line or a terminal emulator in the unzipped folder
 
 **Note:** It's recommended to create a separate [Python virtual environment](https://docs.python.org/3/library/venv.html) and enter it with the appropriate script from `venv/Scripts` folder. 
 
 4. Install requirements from `requirements.txt` with command:
 ```bash
pip install -r requirements.txt
```

### Running from source
Simply run command
- Graphical User Interface:
```bash
python gui.py
```
- Command Line Interface:
```bash
python cli.py
```

### Compiling with [Nuitka](https://github.com/Nuitka/Nuitka)
*It simply works better, faster and stronger.*
1. Create a separate [Python virtual environment](https://docs.python.org/3/library/venv.html) 
2. Enter the venv with the appropriate script from `venv/Scripts` folder
3. Install requirements from `requirements.txt`
4. Install Nuitka [from Nuitka page](https://nuitka.net/doc/download.html) or through pip:
```bash
pip install -U nuitka
```
5. Compile it
- Graphical User Interface:
```bash
python -m nuitka --standalone --include-package=modules --windows-icon-from-ico=assets/kozmadeus.ico --enable-plugin=tk-inter --windows-disable-console --output-filename=kozmadeus-gui.exe gui.py
```
- Command Line Interface:
```bash
python -m nuitka --standalone --include-package=modules --windows-icon-from-ico=assets/kozmadeus.ico --output-filename=kozmadeus-cli.exe cli.py
```
6. Copy `assets` and `templates` folders into the created `gui.dist`/`cli.dist` folder, then within that folder you will find the compiled executable.

# About
## Contributing
Feel free to contribute by posting [Issues](https://github.com/Crowfunder/Kozmadeus/issues) or [Pull Requests](https://github.com/Crowfunder/Kozmadeus/pulls). For Pull Requests, such as another module, feel free to refer to the info on the [Wiki](https://github.com/Crowfunder/Kozmadeus/wiki).

## Credits
- [XanTheDragon](https://github.com/EtiTheSpirit) - Substantive support, a LOT of substantive support. Without Xan I wouldn't be able to pull this whole thing off.

- [Puzovoz](https://github.com/Puzovoz) - Author of Bootshuze, some substantive support as well.

- Kirbeh - Made the current logo.

- Anyone who supported me during the development - Love y'all!

- Whoever gave Kozma her name - Enabled me to make that joke~

## Third Party Libraries
- [pycollada](https://github.com/pycollada/pycollada)
- [PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI)
- [python-wget](https://github.com/steveeJ/python-wget)


