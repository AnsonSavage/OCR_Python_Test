import os
from PIL import Image, ImageOps, ImageEnhance
import argparse
import shutil
import re


def delete_whitespace_after_colon(string):
    segments = string.split(":")
    fixed_segments = []
    for segment in segments:
        reduced_string = ""
        i = 0
        for i in range(len(segment)):
            if segment[i].isdigit():
                break
        reduced_string = segment[i:]
        fixed_segments.append(reduced_string)
    return ":".join(fixed_segments)

parser = argparse.ArgumentParser(description="Crop and process images")
parser.add_argument("input_folder", help="Path to the folder containing the images")
parser.add_argument("output_folder", help="Path to the folder where the processed images will be saved")
args = parser.parse_args()

# Validate the input folder path
input_folder_path = os.path.abspath(args.input_folder)
if not os.path.isdir(input_folder_path):
    print("Error: Input folder does not exist.")
    exit(1)

# Create the output folder if it doesn't exist
output_folder_path = os.path.abspath(args.output_folder)
os.makedirs(output_folder_path, exist_ok=True)

# Path to the folder where the cropped images will be temporarily saved
temp_folder_path = os.path.join(input_folder_path, "temp")

# Create the temporary folder if it doesn't exist
os.makedirs(temp_folder_path, exist_ok=True)

# Padding size in pixels
padding_size = 10

# Scaling factor in the x-axis... (The OCR performs better when the text isn't so stretched)
scaling_factor_x = 0.5

# Loop through all files in the folder
for filename in os.listdir(input_folder_path):
    if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".JPG"):  # Add more file extensions if needed
        # Open the image
        image_path = os.path.join(input_folder_path, filename)
        image = Image.open(image_path)

        # Crop the image
        left = 0
        upper = 0
        right = 972
        lower = 32
        cropped_image = image.crop((left, upper, right, lower))

        # Scale the image in the x-axis
        scaled_width = int(cropped_image.width * scaling_factor_x)
        scaled_height = cropped_image.height
        scaled_image = cropped_image.resize((scaled_width, scaled_height))

        # Invert the colors
        inverted_image = ImageOps.invert(scaled_image)

        # Increase the contrast
        enhancer = ImageEnhance.Contrast(inverted_image)
        contrast_image = enhancer.enhance(2.0)  # Adjust the enhancement factor as needed

        # Add padding
        padded_image = ImageOps.expand(contrast_image, border=padding_size, fill='white')

        # Save the modified image
        output_path = os.path.join(temp_folder_path, filename)
        padded_image.save(output_path)

        # Close the images
        image.close()
        cropped_image.close()
        scaled_image.close()
        inverted_image.close()
        contrast_image.close()
        padded_image.close()

print("Cropping, inverting colors, enhancing contrast, and adding padding completed.")


# NAME IMAGES
import pytesseract

def get_index_of_last_occurrence_of_character(string, character):
    return string.rfind(character)

# Open the image
progress_counter = 0
for filename in os.listdir(temp_folder_path):
    print("Procesing " + filename + " Progress: " + str(progress_counter / len(os.listdir(temp_folder_path)) * 100) + "%")
    progress_counter += 1
    file_path = os.path.join(temp_folder_path, filename)

    image = Image.open(file_path)

    # Perform OCR using pytesseract
    text_from_image = pytesseract.image_to_string(image)

    # Replace the / with a -
    text_from_image = text_from_image.replace("/", "-")
    text_from_image.strip()

    # Remove the \n, \, and \f characters
    text_from_image = text_from_image.replace("\n", "")
    text_from_image = text_from_image.replace("\f", "")
    text_from_image = text_from_image.replace("\\", ":")

    # Ensure that a number follows directly after a colon
    text_from_image = delete_whitespace_after_colon(text_from_image)

    original_path = os.path.join(input_folder_path, filename)
    # Copy this file to the output folder
    output_path = os.path.join(output_folder_path, text_from_image + ".jpg")
    shutil.copyfile(original_path, output_path)

# Remove the temp directory
shutil.rmtree(temp_folder_path)