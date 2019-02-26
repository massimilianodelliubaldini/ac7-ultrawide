import sys, os, shutil, binascii, urllib.request, zipfile, ctypes, math

# Must be in game root folder.
if not os.path.isfile('Ace7Game.exe'):
    wait = input('Ace7Game.exe not found in this folder. Press any key to close...')
    sys.exit(0)

# Get resolution from OS.
u32 = ctypes.windll.user32
u32.SetProcessDPIAware()

[res_w, res_h] = [u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)]
res_y = 1080
res_x = res_w * (res_y / res_h)

# Get confirmation from user.
print('Your screen size appears to be ' + str(res_w) + 'x' + str(res_h) + '.')
prompt = ''
while prompt.lower() != 'y':
    prompt = input('Is that correct? Y to continue, N to cancel:')

    if prompt.lower() == 'n':
        print('Canceled.')
        sys.exit(0)

# Determine FOV hex value.
print('Determining FOV hex value...')
if res_x in [2560, 2304]: # This value is for 2560x1080, 2560x1200 monitors.
    fov_hex = 'AA05333C'
    
elif res_x in [2580, 2322]: # This value is for 3440x1440, 3440x1600 monitors.
    fov_hex = 'EDD1333C'
    
elif res_x in [3840, 3456]: # This value is for dual 16:9, 16:10 monitors.
    fov_hex = 'FCCF653C'
    
elif res_x in [5760, 5184]: # This value is for triple 16:9, 16:10 monitors.
    fov_hex = '707B8B3C'
    
elif res_x in [1920, 1728]: # This value is for single 16:9, 16:10 monitors.
    fov_hex = '35FA0E3C'
    
else:
    print('Unknown resolution or aspect ratio. Quitting.')
    sys.exit(0)

# Back up the game exe.
print('Backing up the game exe...')
if not os.path.isfile('Ace7Game.exe_orig'):
    shutil.copy2('Ace7Game.exe','Ace7Game.exe_orig')

# Overwrite FOV value in game exe.
print('Modifying the game exe...')
with open('Ace7Game.exe','rb+') as exe:

    exe.seek(int('0A03E32A', 16)) # address to remove black bars
    exe.write(binascii.a2b_hex('00'))

    exe.seek(int('02534658', 16)) # address of field of view
    exe.write(binascii.a2b_hex(fov_hex))
    
    exe.close()

# Download 3Dmigoto.
print('Downloading 3Dmigoto...')
tdm_url = 'https://github.com/bo3b/3Dmigoto/releases/download/1.3.14/3Dmigoto-1.3.14.zip'
tdm_zip = tdm_url[tdm_url.rfind('/')+1:]
tdm_dir = tdm_zip[:tdm_zip.rfind('.')]

if not os.path.isfile(tdm_zip):
    urllib.request.urlretrieve(tdm_url, tdm_zip)

# Unpack 3Dmigoto.
print('Unpacking 3Dmigoto...')
zip_ref = zipfile.ZipFile(tdm_zip, 'r')
zip_ref.extractall(tdm_dir)
zip_ref.close()
os.remove(tdm_zip)

# Copy files from x64 folder to game root folder.
print('Installing 3Dmigoto...')
for item in os.listdir(tdm_dir + '/x64'):
    
    tdm_item = tdm_dir + '/x64/' + item
    try:
        if not os.path.exists(item):
            shutil.copytree(tdm_item, item)
    except:
        if not os.path.exists(item):
            shutil.copy2(tdm_item, item)

# Disable shader hunting in config file.
print('Modifying INI config file...')
with open('d3dx.ini','r+') as ini:
    
    ini.seek(10202) # number of bytes to hunting
    ini.write('hunting=0')

    ini.close()

# Set up shader filenames.
github_url = 'https://raw.githubusercontent.com/mpm11011/ac7-ultrawide/master/'
hud_filename = '9958a636cbef5557-ps_replace.txt'
map_filename = 'e6f41464a78a35c4-ps_replace.txt'
char_filename = 'f355a6eae7adfe8e-ps_replace.txt'
map_m7_filename = '27f3e07e177ddf67-ps_replace.txt'
char_m7_filename = 'f904af6042b80b52-ps_replace.txt'
mp_hud_filename = '6dcdbf6042a8a27a-ps_replace.txt'
mp_pause_filename = 'c75a35eef5821976-ps_replace.txt'
mp_map_filename = 'ec51646d13b1fd16-ps_replace.txt'
subtitles_filename = 'da86a094e768f000-vs_replace.txt'
subtitles_hud_checker = 'hudtextfix.ini'

# Download shaders.
print('Downloading shader files...')
urllib.request.urlretrieve(github_url + 'ShaderFixes/' + hud_filename, 'ShaderFixes/' + hud_filename)
urllib.request.urlretrieve(github_url + 'ShaderFixes/' + map_filename, 'ShaderFixes/' + map_filename)
urllib.request.urlretrieve(github_url + 'ShaderFixes/' + char_filename, 'ShaderFixes/' + char_filename)
urllib.request.urlretrieve(github_url + 'ShaderFixes/' + map_m7_filename, 'ShaderFixes/' + map_m7_filename)
urllib.request.urlretrieve(github_url + 'ShaderFixes/' + char_m7_filename, 'ShaderFixes/' + char_m7_filename)
urllib.request.urlretrieve(github_url + 'ShaderFixes/' + mp_hud_filename, 'ShaderFixes/' + mp_hud_filename)
urllib.request.urlretrieve(github_url + 'ShaderFixes/' + mp_pause_filename, 'ShaderFixes/' + mp_pause_filename)
urllib.request.urlretrieve(github_url + 'ShaderFixes/' + mp_map_filename, 'ShaderFixes/' + mp_map_filename)
urllib.request.urlretrieve(github_url + 'ShaderFixes/' + subtitles_filename, 'ShaderFixes/' + subtitles_filename)
urllib.request.urlretrieve(github_url + 'Mods/' + subtitles_hud_checker, 'Mods/' + subtitles_hud_checker)


# Modify shader fix for resolution width.
print('Modifying shader files for resolution...')
delta_x = (res_x - 1920) / 3840 # divide by 1920, then divide by 2.
delta_x = round(delta_x, 4)

with open('ShaderFixes/' + hud_filename,'r+') as hud_file:
    
    hud_file.seek(769) # number of bytes to line needing change
    hud_file.write('  r1.x -= ' + str(delta_x) + ';')

    hud_file.close()

with open('ShaderFixes/' + map_filename,'r+') as map_file:
    
    map_file.seek(1035) # number of bytes to line needing change
    map_file.write('  r0.x -= ' + str(delta_x) + ';')

    map_file.close()

with open('ShaderFixes/' + char_filename,'r+') as char_file:
    
    char_file.seek(1035) # number of bytes to line needing change
    char_file.write('  r0.x -= ' + str(delta_x) + ';')

    char_file.close()

with open('ShaderFixes/' + map_m7_filename,'r+') as map_m7_file:
    
    map_m7_file.seek(1038) # number of bytes to line needing change
    map_m7_file.write('  r1.x -= ' + str(delta_x) + ';')

    map_m7_file.close()

with open('ShaderFixes/' + char_m7_filename,'r+') as char_m7_file:
    
    char_m7_file.seek(1038) # number of bytes to line needing change
    char_m7_file.write('  r1.x -= ' + str(delta_x) + ';')

    char_m7_file.close()

with open('ShaderFixes/' + mp_hud_filename,'r+') as mp_hud_file:
    
    mp_hud_file.seek(769) # number of bytes to line needing change
    mp_hud_file.write('  r1.x -= ' + str(delta_x) + ';')

    mp_hud_file.close()

with open('ShaderFixes/' + mp_pause_filename,'r+') as mp_pause_file:
    
    mp_pause_file.seek(1108) # number of bytes to line needing change
    mp_pause_file.write('  r1.x -= ' + str(delta_x) + ';')

    mp_pause_file.close()

with open('ShaderFixes/' + mp_map_filename,'r+') as mp_map_file:
    
    mp_map_file.seek(1108) # number of bytes to line needing change
    mp_map_file.write('  r1.x -= ' + str(delta_x) + ';')

    mp_map_file.close()

# Modifying subtitles fix for resolution width.
delta_o = (res_w / 2) - ((8/9) * res_h)
delta_o = (2 / res_w) * delta_o
delta_o = round(delta_o, 4)

with open('ShaderFixes/' + subtitles_filename,'r+') as subtitles_file:
    
    subtitles_file.seek(1368) # number of bytes to line needing change
    subtitles_file.write('  o0.x+=' + str(delta_o) + ';')

    subtitles_file.close()
    

wait = input('Script complete. Press any key to close.')
