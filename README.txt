:::::::::                 ::::::::   ::::::::  ::::::::: ::::::::::: 
:+:    :+:               :+:    :+: :+:    :+: :+:    :+:    :+:     
+:+    +:+               +:+        +:+    +:+ +:+    +:+    +:+     
+#++:++#+  +#++:++#++:++ +#++:++#++ +#+    +:+ +#++:++#:     +#+     
+#+                             +#+ +#+    +#+ +#+    +#+    +#+     
#+#                      #+#    #+# #+#    #+# #+#    #+#    #+#     
###                       ########   ########  ###    ###    ###    

========================================================================
 This is an idea I have put together for family members. They like to sort 
 thier media files by date.
 
 So app will grab a directory you give it with the media files, sort through 
 them and copy them into folders titled by the year they 
 were taken.
 
 Any media file that doesn't have the exif data on it's date, will be saved 
 to the 'unsorted' folder in the directory you chose.
 
 
 This sorce also includes Exiftools from `https://github.com/exiftool/exiftool`.


 To run this app currently. You need to just run the `main.py` file from 
 Picture-Sorter directory. As to make sure it finds and utilizes the exiftool.

 Further revisions that have an exe will be run as is, as long as the data folder
 is whereever you run it.

 Things to work on:

    - Need to design the background away from the default gray. As well as an icon
        for the pygame window.
    - Need to implement an 'Create New Folder' within the file dialog.
    - Need to complete the file copy screen, to show when complete.
    - I think I would like to add a config file that allows the app to remember previous
        settings EXAMPLE: Saved media directory.
