## EmulationStation ImageMaker
This Python script combines multiple images into a single composite image based on a configuration file. It processes images from specified directories and applies settings like resizing, effects, and placement. Examples are in the `mixv1` and `tinybest` folders.

![image](https://github.com/user-attachments/assets/378b3c89-2610-4092-b8db-624d8f527ebc) ![render96ex](https://github.com/user-attachments/assets/e8b7575e-e022-4a79-8c7d-a2c75727f31a)


### Features
- Composite Image Creation: Combine thumb, screenshot, logo, and template images onto a single canvas.
- Bezel Effect: Add a gradient bezel around screenshots for a 3D effect. Supports rounded corners.
- Flexible Configuration: Control image sizes, positions, and other settings via ini file.
- Dominant Color Extraction: Automatically adjust bezel color based on the dominant color of screenshots.
- Bounds Checking: Automatically reposition images if they would exit the canvas area.

### Configuration
The script uses a configuration file to define:

- `output_folder`: Directory for saving the resulting images.
- `canvas_size`: Dimensions of the final composite image.
- `compress_level`: Compression level for saving images.
- `bezel_size`, `corner_radius`: Thickness of the bezel and rounded corners.
- Settings for each image type (thumb, screenshot, logo, template) including size, position, and whether they are enabled.

### Usage
Open a terminal next to the script and type `python imgmaker.py <config>` where `<config>` is a filename in the `config/` folder. For example, `python imgmaker.py tinybest` will use the `tinybest.ini` config file.

Mixv1 is configured to use Steam Header images with the floppy template. Matching images must share the same filename. Place your images in the following directories:

`/assets/thumb`  
`/assets/screenshot`  
`/assets/logo`  
`/assets/template`  

Tinybest is configured to use the logo and screenshot only, attempting to mimic the TinyBest Romset artwork style.

## Tips
Sometimes you will have to modify the source images. For example, many logos are much wider than they are tall. To make them scale properly, you will want to crop the surrounding blank space and resize the source logo image to be larger.

There is a `config` folder which contains ini files for `mixv1` and `tinybest`. I have found these are the optimal settings for the two formats.

### Requirements
- Python 3
- PIL (Pillow) for image processing
- colorthief for color extraction

`pip3 install pillow colorthief`

### Contributions
I plan to include alternative artwork solutions in the future. Please feel free to contribute!

### Thanks
- SimplyMav: Floppy Disk template image  
- PortMaster: Screenshots  
- Various authors from [SteamGridDB.com](https://www.steamgriddb.com)  
