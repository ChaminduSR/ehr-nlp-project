import os

def clean_css(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove -ms- prefixes (IE/Edge Legacy)
    # This regex matches -ms- followed by any word character
    # It handles properties like -ms-grid-column and values like -ms-flex
    # But we need to be careful.
    # Simple string replacement might be safer for specific known prefixes.

    # List of prefixes to remove
    prefixes_to_remove = ['-ms-', '-o-', '-moz-']

    new_content = content
    for prefix in prefixes_to_remove:
        # We replace the prefix with nothing, effectively converting
        # -ms-grid-column -> grid-column
        # -moz-box-shadow -> box-shadow
        new_content = new_content.replace(prefix, '')

    # Special handling for IE hacks if any
    # e.g. display: -ms-grid; -> display: grid; (handled above)

    if content != new_content:
        print(f"Cleaned {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print(f"No changes needed for {file_path}")

if __name__ == "__main__":
    css_dir = os.path.join('backend', 'static', 'css')
    for filename in os.listdir(css_dir):
        if filename.endswith('.css'):
            clean_css(os.path.join(css_dir, filename))
