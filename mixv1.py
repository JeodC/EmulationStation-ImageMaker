import os
import configparser
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from colorthief import ColorThief

def get_dominant_color(image_path):
    color_thief = ColorThief(image_path)
    return color_thief.get_color(quality=1)

def find_image_by_name(directory, base_name):
    for file in os.listdir(directory):
        if os.path.splitext(file)[0] == base_name and os.path.splitext(file)[1].lower() in ['.jpg', '.png', '.gif']:
            return os.path.join(directory, file)
    return None

def create_3d_bezel(image, bezel_size, dominant_color, corner_radius):
    # Create a new image for the bezel with a gradient effect
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
    
    # Apply slight blur to the bezel to smooth out the gradient
    bezel_image = bezel_image.filter(ImageFilter.GaussianBlur(radius=2))

    # Paste the original image onto the bezel
    bezel_image.paste(image, (bezel_size, bezel_size), image)

    return bezel_image

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

def create_mix_image(config):
    output_folder = config.get('General', 'output_folder')
    canvas_size = tuple(map(int, config.get('General', 'canvas_size').split(',')))
    compress_level = config.getint('General', 'compress_level')

    thumb_enabled = config.getboolean('Thumb', 'enabled')
    screenshot_enabled = config.getboolean('Screenshot', 'enabled')
    logo_enabled = config.getboolean('Logo', 'enabled')
    template_enabled = config.getboolean('Template', 'enabled')

    safe_width = config.getint('Logo', 'safe_width', fallback=100)
    safe_height = config.getint('Logo', 'safe_height', fallback=100)
    corner_radius = config.getint('Screenshot', 'corner_radius', fallback=0)  # Default to 0 if not provided

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    thumb_files = [os.path.splitext(f)[0] for f in os.listdir('./assets/thumb') if os.path.splitext(f)[1].lower() in ['.jpg', '.png', '.gif']] if thumb_enabled else []
    screenshot_files = [os.path.splitext(f)[0] for f in os.listdir('./assets/screenshot') if os.path.splitext(f)[1].lower() in ['.jpg', '.png', '.gif']] if screenshot_enabled else []
    logo_files = [os.path.splitext(f)[0] for f in os.listdir('./assets/logo') if os.path.splitext(f)[1].lower() in ['.jpg', '.png', '.gif']] if logo_enabled else []
    template_files = [os.path.splitext(f)[0] for f in os.listdir('./assets/template') if os.path.splitext(f)[1].lower() in ['.jpg', '.png', '.gif']] if template_enabled else []

    all_files = set(thumb_files) | set(screenshot_files) | set(logo_files)

    # Sort the file list A-Z
    all_files = sorted(all_files)

    for base_name in all_files:
        try:
            print(f"Processing: {base_name}")

            thumb_image_path = find_image_by_name('./assets/thumb', base_name) if thumb_enabled else None
            screenshot_image_path = find_image_by_name('./assets/screenshot', base_name) if screenshot_enabled else None
            logo_image_path = find_image_by_name('./assets/logo', base_name) if logo_enabled else None
            template_image_path = find_image_by_name('./assets/template', config.get('Template', 'image')) if template_enabled else None

            # Load images
            thumb_image = Image.open(thumb_image_path).convert("RGBA") if thumb_image_path else None
            screenshot_image = Image.open(screenshot_image_path).convert("RGBA") if screenshot_image_path else None
            logo_image = Image.open(logo_image_path).convert("RGBA") if logo_image_path else None
            template_image = Image.open(template_image_path).convert("RGBA") if template_image_path else None

            if thumb_image:
                thumb_size = tuple(map(int, config.get('Thumb', 'size').split(',')))
                thumb_image = thumb_image.resize(thumb_size, Image.Resampling.LANCZOS)
            else:
                print(f"Warning: Thumb image missing for {base_name}")

            if screenshot_image:
                screenshot_size = tuple(map(int, config.get('Screenshot', 'size').split(',')))
                screenshot_image = screenshot_image.resize(screenshot_size, Image.Resampling.LANCZOS)
                bezel_size = config.getint('Screenshot', 'bezel_size')
                dominant_color = get_dominant_color(screenshot_image_path)
                screenshot_image = create_3d_bezel(screenshot_image, bezel_size, dominant_color, corner_radius)
            else:
                print(f"Warning: Screenshot image missing for {base_name}")

            if logo_image:
                try:
                    logo_scale = float(config.get('Logo', 'scale'))
                except ValueError:
                    logo_scale = 1.0  # Default scale factor if not provided

                logo_width, logo_height = logo_image.size
                aspect_ratio = logo_width / logo_height

                if logo_width < safe_width and logo_height < safe_height:
                    new_width, new_height = logo_width, logo_height
                else:
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
                template_image = template_image.resize(template_size, Image.Resampling.LANCZOS)
            else:
                print(f"Warning: Template image missing for {base_name}")

            # Create a new image with transparent canvas
            mix_image = Image.new('RGBA', canvas_size, (0, 0, 0, 0))  # Transparent canvas

            # Calculate and paste images
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
                template_position = (0, 0)
                mix_image.paste(template_image, template_position, template_image)

            # Save the resulting image with compression
            output_path = os.path.join(output_folder, f"{base_name}.png")
            mix_image.save(output_path, format='PNG', compress_level=compress_level)

        except Exception as e:
            print(f"Error processing {base_name}: {e}")

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('mixv1.ini')
    create_mix_image(config)
