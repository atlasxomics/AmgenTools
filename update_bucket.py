import subprocess


api_path = 'config.yml'
worker_path = 'workers/config.yml'
js_path = 'src/static/js/app.38acc792.js'
js_map_path = 'src/static/js/app.38acc792.js.map'
all_paths = [api_path, worker_path, js_map_path, js_path]
def check_bucket(old):
    global all_paths
    count = 0
    for i in all_paths:
        file = open(i, 'r')
        if old in file.read():
            count += 1
            file.close()
    if count == 4:
        return True
    else:
        return False
    
def update_bucket(old, new):
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
print('old_bucket,new_bucket\n')
print('----------------------\n')
old_new_bucket = input('Input Old and New bucket name\n').split(',')
old = old_new_bucket[0].strip()
new = old_new_bucket[1].strip()
print('Checking to see if old bucket is in js files and config files')
valid_bucket = check_bucket(old)

if valid_bucket:
    update_bucket(old, new)
    print('Bucket name is updated check config files for verification')
else:
    print('The bucket was not found in all necessary locations. JS files & Config files in PortableTools and PortableTools/workers\n')
    print('Update could not be made')
