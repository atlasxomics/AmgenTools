import subprocess


js_path = 'src/static/js/app.38acc792.js'
js_map_path = 'src/static/js/app.38acc792.js.map'
all_paths = [js_map_path, js_path]
def check_url(old):
    global all_paths
    count = 0
    for i in all_paths:
        file = open(i, 'r')
        if old in file.read():
            count += 1
            file.close()
    if count == 2:
        return True
    else:
        return False
    
def update_url(old, new):
    global all_paths
    for i in all_paths:
        file = open(i, 'r')
        all_lines = file.read()
        replace = all_lines.replace(old, new)
        file.close()
        
        write_file = open(i, 'w')
        write_file.write(replace)
        write_file.close()


print('Format input as such\n')
print('old_url,new_url\n')
print('----------------------\n')
old_new_url = input('Input Old and New url name\n').split(',')
old = old_new_url[0].strip()
new = old_new_url[1].strip()
print('Checking to see if old url is in js files and config files')
valid_url = check_url(old)

if valid_url:
    update_url(old, new)
    print('url name is updated check config files for verification')
else:
    print('The url was not found in all necessary locations. JS files & Config files in PortableTools and PortableTools/workers\n')
    print('Update could not be made')
