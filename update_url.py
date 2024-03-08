import re

js_path = 'src/static/js/app.38acc792.js'
js_map_path = 'src/static/js/app.38acc792.js.map'
url = ''
all_paths = [js_map_path, js_path]

def check_with_user():
    global url
    global js_map_path
    file = open(js_map_path, 'r')
    all_lines = file.read()
    pattern = r"PROD_SERVER_URL\s*=\s*'([^']+)'"
    match = re.search(pattern, all_lines)
    url = match.group(1)
    return f"Input y if this is the url you want to update\n{url}\n"

def update_url(new):
    global all_paths
    global url
    global all_paths
    for i in all_paths:
        file = open(i, 'r')
        all_lines = file.read()
        replace = all_lines.replace(url, new)
        file.close()
        
        write_file = open(i, 'w')
        write_file.write(replace)
        write_file.close()

check_yes = input(check_with_user())

if check_yes == 'y':

    print('Format input as such\n')
    print('new_url\n')
    print('----------------------\n')
    new_url = input('New url name\n').split(',')
    new = new_url[0].strip()

    update_url(new)
