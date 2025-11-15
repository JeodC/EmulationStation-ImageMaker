import os
import sys
import configparser
import argparse
from PIL import Image, ImageDraw, ImageFilter
from colorthief import ColorThief

required_sections = ['General', 'Thumb', 'Screenshot', 'Logo', 'Template']
required_keys = {
    'General': ['output_folder', 'canvas_size', 'compress_level'],
    'Thumb': ['enabled', 'size', 'position'],
    'Screenshot': ['enabled', 'size', 'position', 'bezel_size', 'corner_radius'],
    'Logo': ['enabled', 'position', 'scale'],
    'Template': ['enabled', 'size', 'position', 'image']
}

# Gets the dominant color from the screenshot to use as the bezel gradient color
def get_dominant_color(image_path):
    color_thief = ColorThief(image_path)
    return color_thief.get_color(quality=1)

# Collects the images to use
def find_image_by_name(directory, base_name):
    for file in os.listdir(directory):
        if os.path.splitext(file)[0] == base_name and os.path.splitext(file)[1].lower() in ['.jpg', '.png', '.gif']:
            return os.path.join(directory, file)
    return None

# Creates the bezel effect
def create_3d_bezel(image, bezel_size, dominant_color, corner_radius):
    width, height = image.size
    bezel_image = Image.new('RGBA', (width + 2 * bezel_size, height + 2 * bezel_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bezel_image)

    # Draw gradient border
    for i in range(bezel_size):
        color = (
            int(dominant_color[0] * (1 - i / bezel_size)),
            int(dominant_color[1] * (1 - i / bezel_size)),
            int(dominant_color[2] * (1 - i / bezel_size)),
            int(255 * (1 - i / bezel_size))
        )
        draw.rounded_rectangle(
            [i, i, width + 2 * bezel_size - i, height + 2 * bezel_size - i],
            radius=corner_radius,
            outline=color,
            width=1
        )

    bezel_image = bezel_image.filter(ImageFilter.GaussianBlur(radius=2))
    bezel_image.paste(image, (bezel_size, bezel_size), image)
    return bezel_image

# Checks the position of images to ensure they remain entirely within the canvas
def bounds_check(position, image_size, canvas_size):
    x, y = position
    img_width, img_height = image_size
    canvas_width, canvas_height = canvas_size

    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x + img_width > canvas_width:
        x = canvas_width - img_width
    if y + img_height > canvas_height:
        y = canvas_height - img_height

    return (x, y)

# Creates the image
def create_image(config):
    output_folder = config.get('General', 'output_folder')
    canvas_size = tuple(map(int, config.get('General', 'canvas_size').split(',')))
    compress_level = config.getint('General', 'compress_level')
    skip_existing = config.getboolean('General', 'skip_existing', fallback=False)
    template_enabled = config.getboolean('Template', 'enabled')
    always_on = config.getboolean('Template', 'always_on', fallback=True)
    thumb_enabled = config.getboolean('Thumb', 'enabled')
    screenshot_enabled = config.getboolean('Screenshot', 'enabled')
    corner_radius = config.getint('Screenshot', 'corner_radius', fallback=0)
    logo_enabled = config.getboolean('Logo', 'enabled')
    resize_enabled = config.getboolean('Resize', 'enabled', fallback=False)
    resize_size = tuple(map(int, config.get('Resize', 'size').split(','))) if resize_enabled else None

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    thumb_files = [os.path.splitext(f)[0] for f in os.listdir('./assets/thumb') if os.path.splitext(f)[1].lower() in ['.jpg', '.png', '.gif']] if thumb_enabled else []
    screenshot_files = [os.path.splitext(f)[0] for f in os.listdir('./assets/screenshot') if os.path.splitext(f)[1].lower() in ['.jpg', '.png', '.gif']] if screenshot_enabled else []
    logo_files = [os.path.splitext(f)[0] for f in os.listdir('./assets/logo') if os.path.splitext(f)[1].lower() in ['.jpg', '.png', '.gif']] if logo_enabled else []
    template_files = [os.path.splitext(f)[0] for f in os.listdir('./assets/template') if os.path.splitext(f)[1].lower() in ['.jpg', '.png', '.gif']] if template_enabled else []
    all_files = set(thumb_files) | set(screenshot_files) | set(logo_files)
    all_files = sorted(all_files)

    if skip_existing:
        print(f"Skipping existing images.")
    for base_name in all_files:
        try:
            output_path = os.path.join(output_folder, f"{base_name}.png")
            if skip_existing and os.path.exists(output_path):
                continue

            print(f"Processing: {base_name}")

            thumb_image_path = find_image_by_name('./assets/thumb', base_name) if thumb_enabled else None
            screenshot_image_path = find_image_by_name('./assets/screenshot', base_name) if screenshot_enabled else None
            logo_image_path = find_image_by_name('./assets/logo', base_name) if logo_enabled else None
            template_image_path = find_image_by_name('./assets/template', config.get('Template', 'image')) if template_enabled else None

            thumb_image = Image.open(thumb_image_path).convert("RGBA") if thumb_image_path else None
            screenshot_image = Image.open(screenshot_image_path).convert("RGBA") if screenshot_image_path else None
            logo_image = Image.open(logo_image_path).convert("RGBA") if logo_image_path else None
            template_image = Image.open(template_image_path).convert("RGBA") if template_image_path else None

            if thumb_image:
                thumb_size = tuple(map(int, config.get('Thumb', 'size').split(',')))
                thumb_image = thumb_image.resize(thumb_size, Image.Resampling.LANCZOS)
            else:
                if not always_on:
                    template_image = None
                else:
                    print(f"Warning: Thumb image missing for {base_name}")

            if screenshot_image:
                # Normalize the screenshot: convert + resize + overwrite
                screenshot_norm = screenshot_image.convert("RGBA")
                screenshot_norm = screenshot_norm.resize((640, 480), Image.Resampling.LANCZOS)

                # overwrite original file as PNG
                base = os.path.splitext(screenshot_image_path)[0]
                new_path = base + ".png"
                screenshot_norm.save(new_path, format="PNG")

                # Reload normalized screenshot so it follows config sizing
                screenshot_image = Image.open(new_path).convert("RGBA")

                # Now apply config-driven screenshot resizing (original behavior)
                screenshot_size = tuple(map(int, config.get('Screenshot', 'size').split(',')))
                screenshot_image = screenshot_image.resize(screenshot_size, Image.Resampling.LANCZOS)

                # Bezel
                bezel_size = config.getint('Screenshot', 'bezel_size')
                dominant_color = get_dominant_color(new_path)
                screenshot_image = create_3d_bezel(screenshot_image, bezel_size, dominant_color, corner_radius)
            else:
                print(f"Warning: Screenshot image missing for {base_name}")

            if logo_image:
                try:
                    logo_scale = float(config.get('Logo', 'scale'))
                except ValueError:
                    logo_scale = 1.0

                logo_width, logo_height = logo_image.size
                aspect_ratio = logo_width / logo_height

                new_width = int(canvas_size[0] * logo_scale)
                new_height = int(new_width / aspect_ratio)

                if new_height > canvas_size[1]:
                    new_height = canvas_size[1]
                    new_width = int(new_height * aspect_ratio)

                logo_image = logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                print(f"Warning: Logo image missing for {base_name}")

            if template_image:
                template_size = tuple(map(int, config.get('Template', 'size').split(',')))
                template_position = tuple(map(int, config.get('Template', 'position').split(',')))
                template_image = template_image.resize(template_size, Image.Resampling.LANCZOS)

            mix_image = Image.new('RGBA', canvas_size, (0, 0, 0, 0))

            if screenshot_image:
                screenshot_position = tuple(map(int, config.get('Screenshot', 'position').split(',')))
                screenshot_position = bounds_check(screenshot_position, screenshot_image.size, canvas_size)
                mix_image.paste(screenshot_image, screenshot_position, screenshot_image)

            if logo_image:
                logo_position = tuple(map(int, config.get('Logo', 'position').split(',')))
                logo_position = bounds_check(logo_position, logo_image.size, canvas_size)
                mix_image.paste(logo_image, logo_position, logo_image)

            if thumb_image:
                thumb_position = tuple(map(int, config.get('Thumb', 'position').split(',')))
                thumb_position = bounds_check(thumb_position, thumb_image.size, canvas_size)
                mix_image.paste(thumb_image, thumb_position, thumb_image)

            if template_image:
                template_position = bounds_check(template_position, template_image.size, canvas_size)
                mix_image.paste(template_image, template_position, template_image)

            # Resize final image if required
            if resize_enabled and resize_size:
                print(f"Resizing image {base_name}")
                mix_image = mix_image.resize(resize_size, Image.Resampling.LANCZOS)

            mix_image.save(output_path, format='PNG', compress_level=compress_level)

        except Exception as e:
            print(f"Error processing {base_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Image maker script.')
    parser.add_argument('config_file', type=str, help='Name of the configuration file (without the .ini extension).')
    parser.add_argument('--config_dir', type=str, default='config', help='Directory where the configuration files are located.')
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config_file_path = os.path.join(args.config_dir, f"{args.config_file}.ini")
    
    # Error checking -- does file exist?
    if not os.path.exists(config_file_path):
        print(f"Error: The specified configuration file does not exist: {config_file_path}")
        sys.exit(1)
    ## Error checking -- is file valid?
    config.read(config_file_path)
    print(f"Sections found in config: {config.sections()}")
    for section in required_sections:
        if not config.has_section(section):
            print(f"Error: Missing required section [{section}] in the configuration file.")
            sys.exit(1)

        for key in required_keys[section]:
            if not config.has_option(section, key):
                print(f"Error: Missing required key '{key}' in section [{section}] of the configuration file.")
                sys.exit(1) 
    print(f"Using config {config_file_path}")
    create_image(config)
    print(f"Completed processing images.")