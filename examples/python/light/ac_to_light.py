from PIL import Image, ImageDraw  # Importing necessary libraries from PIL for image manipulation
import imageio

# Read the content of the file "ac.txt" and store it as a string
with open("ac.txt", "r") as file:
    content = file.read()

# Convert the file content into binary format (8-bit representation for each character)
binary_content = ''.join(format(ord(char), '08b') for char in content)

# Define the size of each square (each pixel will be represented as a 20x20 square)
square_size = 20

# Create a list to store individual frames of the animation
frames = []

# Generate an image for each binary character in the content
for bit in binary_content:
    # Create a new square image (in RGB format, default color is white)
    img = Image.new("RGB", (square_size, square_size), "white")
    draw = ImageDraw.Draw(img)

    # Determine the color based on the current bit (1 = white, 0 = black)
    color = "white" if bit == "1" else "black"
    draw.rectangle(
        [
            0, 0,  # Top-left corner
            square_size - 1, square_size - 1  # Bottom-right corner
        ],
        fill=color  # Fill the square with the selected color
    )

    # Append the created image (frame) to the frames list
    frames.append(img)

# Define the output file name for the GIF
output_gif = "binary_animation.gif"

# Save the frames as an animated GIF
frames[0].save(
    output_gif,  # Output file name
    save_all=True,  # Save all frames in the GIF
    append_images=frames[1:],  # Add all subsequent frames
    duration=100,  # Display each frame for 100 milliseconds
    loop=0  # Loop the animation indefinitely
)

# Print a confirmation message after the GIF is created
print(f"GIF created: {output_gif}")
