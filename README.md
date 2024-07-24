## EmulationStation ImageMaker
This Python script combines multiple images into a single composite image based on a configuration file. It processes images from specified directories and applies settings like resizing, effects, and placement. Examples are in the `mixv1` folder.

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
Matching images must share the same filename. Place your images in the following directories:

`/assets/thumb`  
`/assets/screenshot`  
`/assets/logo`  
`/assets/template`  

Create or update the `mixv1.ini` file with your desired settings and run the script to generate composite images in the specified output folder.

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