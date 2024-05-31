import os

def save_levels_to_files(input_filename, output_directory, max_levels=100):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    with open(input_filename, 'r') as file:
        content = file.read()

    # Split the content by semicolon indicating new levels
    levels = content.split('\n;')
    if levels[0].startswith(';'):
        levels[0] = levels[0][1:]

    # Process and save each level
    for i, level in enumerate(levels[:max_levels]):
        # Remove leading newlines and the first two lines
        lines = level.strip().split('\n')[2:]
        level_content = '\n'.join(lines)
        
        # Define the output filename
        output_filename = os.path.join(output_directory, f'level_{i+1}.txt')
        with open(output_filename, 'w') as output_file:
            output_file.write(level_content)


input_filename = 'levels/MicrobanIII.txt'
output_directory = 'levels'

save_levels_to_files(input_filename, output_directory)