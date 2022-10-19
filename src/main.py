import os, sys, subprocess, pygame, pygame_gui, threading, exiftool, shutil, time
from pathlib import Path
from collections import deque
from pygame_gui.elements import UIButton, UIStatusBar, UILabel
from pygame_gui.windows import UIFileDialog


"""
    This is just a base class to define the window elements.

"""
class Window:
    def __init__(self):
        self.resolution = 800,600
        self.fullscreen = False

        pygame.init()
        icon = None
        # pygame.display.set_icon(icon)
        pygame.display.set_caption('Picture Sorter')


"""
    This is the main class. Here we utilize pygame_gui to navigate and execute the script.

"""
class App:
    def __init__(self):
        # This is the boolen for the runtime of the app.
        self.running = True 
        # This is the initial state that the gui will load at startup.
        self.state = 'first'
        # This will load some gui specific items once so they don't cycle over and over.
        self.initized = False
        # This will create a temp directory for the runtime of the app. It will be deleted on close.
        self.temp_dir()
        # This is the variable used for the media files you have
        self.output = False
        # This is the variable used for where you want the variables to go.
        self.input = False
        # A boolean for the runtime to know when to start the install thread.
        self.installing = False
        # This is a populated list of all mediafiles. This will help determine the percentage in which the 
        #       progress bar will move.
        self.res = []
        # This determines the folders in which already exists and / or need to be created for the files in
                # self.res
        self.date_lists = []

    #  The temp directory function
    def temp_dir(self):
        try:
            os.mkdir('./temp')
            self.temp = './temp'
        except:
            try:
                self.temp = './temp'
            except:
                None
        # This will search your system for all disk drives and then will create symlinks to them within the temp folder
        # This is used for the file dialog as the landing page so you can access a USB easily.
        drivelist = subprocess.Popen('wmic logicaldisk get name,description', shell=True, stdout=subprocess.PIPE)
        drivelisto, err = drivelist.communicate()
        driveLines = str(drivelisto).split(':')
        for item in driveLines:
            if item[-1] == "'":
                pass
            else: 
                # creates the symlink Junctions
                subprocess.check_call('mklink /J "%s" "%s"' % (f'./temp/{item[-1]}', f'{item[-1]}:/'), shell=True)
            


    #  This defines what gui elements need to be on the screen during each self.state.
    def recreate_ui(self):
        self.manager.set_window_resolution(self.screen.resolution)
        
        self.manager.clear_and_reset()

        self.background_surface = pygame.Surface(self.screen.resolution)
        # self.background_image = pygame.image.load('./data/images/background.jpg')
        # self.background_surface.blit(self.background_image, (0, 0))
        self.background_surface.fill(self.manager.get_theme().get_colour('dark_bg'))
        if self.state == 'first':
            self.output_folderB = UIButton(pygame.Rect(200, 400, 400, 50),
                                  f'Select Folder with Photos',
                                  self.manager)
            self.input_folderB = UIButton(pygame.Rect(200, 460, 400, 50),
                                  f'Select Folder to save Photos',
                                  self.manager)  
            self.runB =          UIButton(pygame.Rect(325, 520, 150, 50),
                                  f'GO!',
                                  self.manager) 
        if self.state == 'second':
            self.progress_bar = UIStatusBar(pygame.Rect(125, 500, 550, 50),
                                            manager=self.manager)
            self.progress = UILabel(pygame.Rect(550, 555, 150, 50),
                                     "",
                                     self.manager)
            self.title = UILabel(pygame.Rect(120, 430, 250, 80),
                                 "Reading files..",
                                 self.manager)

    # This will process all pygame events. In particular gui events. Some events still need to be run 
    #   during the run function to avoid locking up.
    def process_events(self):
        
        for x in pygame.event.get():
            if x.type == pygame.QUIT:
                temp = os.listdir('./temp')
                for folder in temp:
                    print(folder)
                    # Deletes the temp folder on close of the application.
                    os.removedirs(f'./temp/{folder}')
                self.running = False
            
            if x.type == pygame_gui.UI_BUTTON_PRESSED:
                if x.ui_element == self.output_folderB:

                    self.output_picked = UIFileDialog(pygame.Rect(175, 125, 450, 350),
                                          manager=self.manager,
                                          window_title='Choose Folder with Photos..',
                                          initial_file_path=f'{self.temp}',
                                          allow_picking_directories=True)
                    self.output = True

                if x.ui_element == self.input_folderB:

                    self.input_picked = UIFileDialog(pygame.Rect(175, 125, 450, 350),
                                          manager=self.manager,
                                          window_title='Choose Folder with Photos..',
                                          initial_file_path=f'{self.temp}',
                                          allow_picking_directories=True)
                    self.input = True
                
                if x.ui_element == self.runB:

                    self.state = 'second'
                    self.recreate_ui()
                    self.installing = True

            if x.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                if self.output == True:
                    self.outputPath = x.text
                    self.output_folderB.text = x.text
                    self.output_folderB.rebuild()
                    self.output = False
                elif self.input == True:
                    self.inputPath = x.text
                    self.input_folderB.text = x.text
                    self.input_folderB.rebuild()
                    self.input = False

            self.manager.process_events(x)

    # This reads the files in the selected directory as well as files in subdirectories.
    def file_reading(self): 
        for (dirpath, dir_names, files) in os.walk(self.outputPath):
            self.res.extend(os.path.join(dirpath, x) for x in files)
        self.list_enumerate()

    # This then enumerates the date_lists list, which determines if there is already existing folders
    def list_enumerate(self):
        
        self.photo_folder = self.inputPath
        for dirs in os.listdir(self.photo_folder):
            if len(dirs) == 4:
                self.date_lists.append(dirs)
        self.file_copy()

    # This then starts the copying function. It will create folders within the directory chosen if 
    #       the folder doesn't exist in date_lists
    def file_copy(self):
        self.title.text = 'Copying files..'
        self.title.rebuild()
        value = len(self.res)
        percent = 1/value

        path = os.getcwd()
        # This adds the exiftool to the path, so then it is read by python and able to be executed.
        #   This is only added for this runtime.
        os.environ['PATH'] += f';{path}\\data\\exiftool'

        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(self.res)
        for d in metadata:
            try:
                # This is looking for image files and thier Date/Time/Origin
                test = d["EXIF:DateTimeOriginal"]
                if test[0:4] in self.date_lists:
                    shutil.copy(d["SourceFile"], f'{self.photo_folder}/{test[0:4]}')
                else:
                    self.date_lists.append(test[0:4])
                    os.makedirs(f'{self.photo_folder}/{test[0:4]}')
                    shutil.copy(d["SourceFile"], f'{self.photo_folder}/{test[0:4]}')
            except:
                try:
                    # This is looking for video files and their Date/Time/Origin
                    test = d["QuickTime:CreateDate"]
                    if test[0:4] in self.date_lists:
                        # In my tests, sometimes the video files have Origin date of 0000/00/00
                        #   This will create a folder at 0000. This will skip those files and put them in the 
                        #   unsorted folder instead
                        if test[0:4] == '0000':
                            shutil.copy(d["SourceFile"], f'{self.photo_folder}/unsorted')

                        else:
                            shutil.copy(d["SourceFile"], f'{self.photo_folder}/{test[0:4]}')
                    else:
                        # This will make the folders if they don't exist in the date_lists
                        if test[0:4] == '0000':
                            try:
                                os.makedirs(f'{self.photo_folder}/unsorted')
                                shutil.copy(d["SourceFile"], f'{self.photo_folder}/unsorted')
                            except:
                                shutil.copy(d["SourceFile"], f'{self.photo_folder}/unsorted')
                        else:        
                            self.date_lists.append(test[0:4])
                            os.makedirs(f'{self.photo_folder}/{test[0:4]}')
                            shutil.copy(d["SourceFile"], f'{self.photo_folder}/{test[0:4]}')
                except:
                    try:
                        os.makedirs(f'{self.photo_folder}/unsorted')
                        shutil.copy(d["SourceFile"], f'{self.photo_folder}/unsorted')
                    except:
                        shutil.copy(d["SourceFile"], f'{self.photo_folder}/unsorted')
            # This is for the GUI so you can see the progress bar moving for each file sorted.
            self.progress_bar.percent_full += percent
            self.progress_bar.rebuild()
        # Once the for loop has been completed, it will complete the progress bar. Just incase their is a 
        #   disrepency in the information.
        self.progress_bar.percent_full = 1
        self.progress_bar.rebuild()

    # This is the main runtime of the applicaton.
    def run(self):
        while self.running:
            if self.initized == False:
                self.screen = Window()
                
                if self.screen.fullscreen:
                    self.surface = pygame.display.set_mode(self.screen.resolution, pygame.FULLSCREEN)
                else:
                    self.surface = pygame.display.set_mode(self.screen.resolution)
                
                self.background_surface = None

                self.manager = pygame_gui.UIManager(self.screen.resolution, 'data/themes/default.json')

                self.manager.preload_fonts([{'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
                                        {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
                                        {'name': 'fira_code', 'point_size': 10, 'style': 'italic'},
                                        {'name': 'fira_code', 'point_size': 14, 'style': 'italic'},
                                        {'name': 'fira_code', 'point_size': 14, 'style': 'bold'}
                                        ])
                
                self.recreate_ui()
                # Determines fps of the application.
                self.clock = pygame.time.Clock()
                self.time_delta_stack = deque([])
                self.initized = True
                
            self.time_delta = self.clock.tick(240)/1000.0

            self.time_delta_stack.append(self.time_delta)

            if len(self.time_delta_stack) > 2000:
                self.time_delta_stack.popleft()

            # This will call all the GUI events
            self.process_events()

            # This is an event that can't be in a seperate function as it will lock up.
            # It will start a new thread so that the GUI can still function while information is being read.
            if self.installing == True:
                if self.state == 'second':
                    t2 = threading.Thread(target=self.file_reading)
                    t2.start()
                    self.installing = False
            
            # Updates all the GUI specific elements.
            self.manager.update(self.time_delta)

            # Blits the image / color to the background
            self.surface.blit(self.background_surface, (0, 0))

            # This draws all the GUI elements to the window surface.
            self.manager.draw_ui(self.surface)

            # Standard pygame display update.
            pygame.display.update()


if __name__ == '__main__':
    app = App()
    app.run()