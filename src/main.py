import os, sys, subprocess, pygame, pygame_gui, threading, exiftool, shutil, time
from pathlib import Path
from collections import deque
from pygame_gui.elements import UIButton, UIStatusBar, UILabel
from pygame_gui.windows import UIFileDialog



class Window:
    def __init__(self):
        self.resolution = 800,600
        self.fullscreen = False

        pygame.init()
        icon = None
        # pygame.display.set_icon(icon)
        pygame.display.set_caption('Picture Sorter')


class App:
    def __init__(self):
        self.running = True
        self.state = 'first'
        self.initized = False
        self.temp_dir()
        self.output = False
        self.input = False
        self.installing = False
        self.res = []
        self.date_lists = []
    def temp_dir(self):
        try:
            os.mkdir('./temp')
            self.temp = './temp'
        except:
            try:
                self.temp = './temp'
            except:
                None

        drivelist = subprocess.Popen('wmic logicaldisk get name,description', shell=True, stdout=subprocess.PIPE)
        drivelisto, err = drivelist.communicate()
        driveLines = str(drivelisto).split(':')
        for item in driveLines:
            if item[-1] == "'":
                pass
            else: 
                subprocess.check_call('mklink /J "%s" "%s"' % (f'./temp/{item[-1]}', f'{item[-1]}:/'), shell=True)
            



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

    
    def process_events(self):
        
        for x in pygame.event.get():
            if x.type == pygame.QUIT:
                temp = os.listdir('./temp')
                for folder in temp:
                    print(folder)
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

    def file_reading(self): 
        for (dirpath, dir_names, files) in os.walk(self.outputPath):
            self.res.extend(os.path.join(dirpath, x) for x in files)
        self.list_enumerate()

    def list_enumerate(self):
        
        self.photo_folder = self.inputPath
        for dirs in os.listdir(self.photo_folder):
            if len(dirs) == 4:
                self.date_lists.append(dirs)
        self.file_copy()

    def file_copy(self):
        self.title.text = 'Copying files..'
        self.title.rebuild()
        value = len(self.res)
        percent = 1/value

        path = os.getcwd()

        os.environ['PATH'] += f';{path}\\data\\exiftool'

        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(self.res)
        for d in metadata:
            try:
                test = d["EXIF:DateTimeOriginal"]
                if test[0:4] in self.date_lists:
                    shutil.copy(d["SourceFile"], f'{self.photo_folder}/{test[0:4]}')
                else:
                    self.date_lists.append(test[0:4])
                    os.makedirs(f'{self.photo_folder}/{test[0:4]}')
                    shutil.copy(d["SourceFile"], f'{self.photo_folder}/{test[0:4]}')
            except:
                try:
                    test = d["QuickTime:CreateDate"]
                    if test[0:4] in self.date_lists:
                        if test[0:4] == '0000':
                            shutil.copy(d["SourceFile"], f'{self.photo_folder}/unsorted')

                        else:
                            shutil.copy(d["SourceFile"], f'{self.photo_folder}/{test[0:4]}')
                    else:
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
            self.progress_bar.percent_full += percent
            self.progress_bar.rebuild()
        self.progress_bar.percent_full = 1
        self.progress_bar.rebuild()

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

            self.clock = pygame.time.Clock()
            self.time_delta_stack = deque([])
            self.initized = True
            self.time_delta = self.clock.tick(240)/1000.0

            self.time_delta_stack.append(self.time_delta)

            if len(self.time_delta_stack) > 2000:
                self.time_delta_stack.popleft()

            self.process_events()

            if self.installing == True:
                if self.state == 'second':
                    t2 = threading.Thread(target=self.file_reading)
                    t2.start()
                    self.installing = False

            self.manager.update(self.time_delta)

            self.surface.blit(self.background_surface, (0, 0))

            self.manager.draw_ui(self.surface)

            pygame.display.update()


def test():
    global res
    res = []
    

    for (dirpath, dir_names, files) in os.walk(r'C:\Users\Sam\Downloads\iCloud Photos from Samuel Smollen\iCloud Photos from Samuel Smollen'):
        res.extend(os.path.join(dirpath, x) for x in files)
    # image = Image.open("C:\\Users\\Sam\\Downloads\\iCloud Photos from Samuel Smollen\\iCloud Photos from Samuel Smollen\\IMG_0026.JPG", 'r')
    # exif = image.getexif()
    # date_taken = exif.get(306)

    # print(date_taken)

def test2():
    global res
    path = os.getcwd()
    photo_folder = Path('./photos')
    if photo_folder.is_dir():
        None
    else:
        os.makedirs('./photos')
    os.environ['PATH'] += f';{path}\\data\\exiftool'
    date_lists = []
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(res)
    for d in metadata:
        try:
            test = d["EXIF:DateTimeOriginal"]
            if test[0:4] in date_lists:
                shutil.copy(d["SourceFile"], f'./{photo_folder}/{test[0:4]}')
            else:
                date_lists.append(test[0:4])
                os.makedirs(f'./{photo_folder}/{test[0:4]}')
                shutil.copy(d["SourceFile"], f'./{photo_folder}/{test[0:4]}')
        except:
            try:
                test = d["QuickTime:CreateDate"]
                if test[0:4] in date_lists:
                    if test[0:4] == '0000':
                        shutil.copy(d["SourceFile"], f'./{photo_folder}/unsorted')

                    else:
                        shutil.copy(d["SourceFile"], f'./{photo_folder}/{test[0:4]}')
                else:
                    if test[0:4] == '0000':
                        try:
                            os.makedirs(f'./{photo_folder}/unsorted')
                            shutil.copy(d["SourceFile"], f'./{photo_folder}/unsorted')
                        except:
                            shutil.copy(d["SourceFile"], f'./{photo_folder}/unsorted')
                    else:        
                        date_lists.append(test[0:4])
                        os.makedirs(f'./{photo_folder}/{test[0:4]}')
                        shutil.copy(d["SourceFile"], f'./{photo_folder}/{test[0:4]}')
            except:
                try:
                    os.makedirs(f'./{photo_folder}/unsorted')
                    shutil.copy(d["SourceFile"], f'./{photo_folder}/unsorted')
                except:
                    shutil.copy(d["SourceFile"], f'./{photo_folder}/unsorted')



def test3():
    global data_lists
    for dirs in os.listdir(r'C:\Users\Sam\Desktop\Python_Stuff\Under-Contruction\Picture Sorter\photos'):
        if len(dirs) == 4:
            data_lists.append(dirs)


if __name__ == '__main__':
    app = App()
    app.run()