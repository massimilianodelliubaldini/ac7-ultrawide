import sys, os, shutil, binascii, urllib.request, zipfile, ctypes, math, glob
from datetime import datetime

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
# First 4 bytes actually determine FOV, last 2 bytes is explained below.
print('Determining FOV hex value...')
if res_x in [2560, 2304]: # This value is for 2560x1080, 2560x1200 monitors.
    fov_hex = 'AA 05 33 3C D8 F5'
    
elif res_x in [2580, 2322]: # This value is for 3440x1440, 3440x1600 monitors.
    fov_hex = 'ED D1 33 3C D8 F5'
    
elif res_x in [3840, 3456]: # This value is for dual 16:9, 16:10 monitors.
    fov_hex = 'FC CF 65 3C D8 F5'
    
elif res_x in [5760, 5184]: # This value is for triple 16:9, 16:10 monitors.
    fov_hex = '70 7B 8B 3C D8 F5'
    
elif res_x in [1920, 1728]: # This value is for single 16:9, 16:10 monitors.
    fov_hex = '35 FA 0E 3C D8 F5'
    
else:
    print('Unknown resolution or aspect ratio. Quitting.')
    sys.exit(0)

# Back up the game exe.
print('Backing up the game exe...')
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

if not os.path.isfile('Ace7Game.exe_orig'):
    shutil.copy2('Ace7Game.exe','Ace7Game.exe_' + timestamp)

# Edit the game exe.
print('Modifying the game exe...')
with open('Ace7Game.exe','rb+') as exe:

    exe_data = exe.read()
    exe.close()

# The value '41 2C 01 4C 89 CB 0F 29' is only found once in the EXE.
exe_data = exe_data.replace(bytes.fromhex('41 2C 01 4C 89 CB 0F 29'), bytes.fromhex('41 2C 00 4C 89 CB 0F 29')) # Removes black bars.

# '35 FA 0E 3C' is the default FOV value we want to replace, but it is found 6 times in the EXE, and we only want to replace it once. 
# How do we know which one to replace? 'D8 F5' happens to follow that value at the FOV address, and it doesn't follow any other addresses with the same value.
# So when we search for '35 FA 0E 3C D8 F5' we only find it once, which is exactly what we need.
exe_data = exe_data.replace(bytes.fromhex('35 FA 0E 3C D8 F5'), bytes.fromhex(fov_hex)) # Fixes field of view.

with open('Ace7Game.exe','wb') as exe:
    
    exe.write(exe_data);
    exe.close()

# Check to make sure nothing broke by comparing number of bytes modified. Should only be 4.
print('Verifying the game exe...')

bytes_changed = 0
address = 0
with open('Ace7Game.exe','rb+') as exe_new:
    with open('Ace7Game.exe_' + timestamp,'rb+') as exe_old:

        exe_new_byte = exe_new.read(1)
        exe_old_byte = exe_old.read(1)

        while exe_new_byte:
            if exe_new_byte != exe_old_byte:
                
                bytes_changed += 1
                print('Old byte: ' + str(exe_old_byte) + ', New byte: ' + str(exe_new_byte) + ', at address: ' + str(address))

            exe_new_byte = exe_new.read(1)
            exe_old_byte = exe_old.read(1)

            address += 1

        exe_old.close()
    exe_new.close()
    
if bytes_changed > 4:
    print('WARNING: More bytes were changed than expected! Recommend restoring exe from backup and performing those changes manually...')
elif bytes_changed < 4:
    print('WARNING: Fewer bytes were changed than expected! Recommend restoring exe from backup and performing those changes manually...')
else:
    print('Verification successful.')

# Check for 3Dmigoto zip file.
print('Checking for 3Dmigoto zip file...')
tdm_regex = '3Dmigoto-*.zip'
tdm_list = glob.glob(tdm_regex)

if not tdm_list:
    print('3Dmigoto zip file not found. Quitting.')
    sys.exit(0)

tdm_zip = tdm_list[0]
tdm_dir = tdm_zip[:tdm_zip.rfind('.')]

# Unpack 3Dmigoto.
print('Unpacking ' + tdm_zip + '...')
zip_ref = zipfile.ZipFile(tdm_zip, 'r')
zip_ref.extractall(tdm_dir)
zip_ref.close()

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

# Create Mods and ShaderFixes folders if they somehow don't exist.
if not os.path.isdir('Mods'):
    os.mkdir('Mods')

if not os.path.isdir('ShaderFixes'):
    os.mkdir('ShaderFixes')

# Set up shader filenames.
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

# Find and modify shaders.
print('Modifying shader files...')

delta_x = (res_x - 1920) / 3840 # divide by 1920, then divide by 2.
delta_x = round(delta_x, 4)

delta_o = 1 - ((16/9) * (res_h/res_w))
delta_o = round(delta_o, 4)

if not os.path.exists('ShaderFixes/' + hud_filename):
    print('Shader fix for HUD not found! Missing ' + hud_filename + '.')

else:
    with open('ShaderFixes/' + hud_filename,'r+') as hud_file:
        
        hud_file.seek(769) # number of bytes to line needing change
        hud_file.write('  r1.x -= ' + str(delta_x) + ';')
        hud_file.close()

if not os.path.exists('ShaderFixes/' + map_filename):
    print('Shader fix for minimap not found! Missing ' + map_filename + '.')

else:
    with open('ShaderFixes/' + map_filename,'r+') as map_file:
        
        map_file.seek(1035) # number of bytes to line needing change
        map_file.write('  r0.x -= ' + str(delta_x) + ';')
        map_file.close()

if not os.path.exists('ShaderFixes/' + char_filename):
    print('Shader fix for character portraits not found! Missing ' + char_filename + '.')

else:
    with open('ShaderFixes/' + char_filename,'r+') as char_file:
        
        char_file.seek(1035) # number of bytes to line needing change
        char_file.write('  r0.x -= ' + str(delta_x) + ';')
        char_file.close()

if not os.path.exists('ShaderFixes/' + map_m7_filename):
    print('Shader fix for glitchy minimap not found! Missing ' + map_m7_filename + '.')

else:
    with open('ShaderFixes/' + map_m7_filename,'r+') as map_m7_file:
        
        map_m7_file.seek(1038) # number of bytes to line needing change
        map_m7_file.write('  r1.x -= ' + str(delta_x) + ';')
        map_m7_file.close()

if not os.path.exists('ShaderFixes/' + char_m7_filename):
    print('Shader fix for glitchy character portraits not found! Missing ' + char_m7_filename + '.')

else:
    with open('ShaderFixes/' + char_m7_filename,'r+') as char_m7_file:
        
        char_m7_file.seek(1038) # number of bytes to line needing change
        char_m7_file.write('  r1.x -= ' + str(delta_x) + ';')
        char_m7_file.close()


if not os.path.exists('ShaderFixes/' + mp_hud_filename):
    print('Shader fix for multiplayer HUD not found! Missing ' + mp_hud_filename + '.')

else:
    with open('ShaderFixes/' + mp_hud_filename,'r+') as mp_hud_file:
        
        mp_hud_file.seek(769) # number of bytes to line needing change
        mp_hud_file.write('  r1.x -= ' + str(delta_x) + ';')
        mp_hud_file.close()


if not os.path.exists('ShaderFixes/' + mp_pause_filename):
    print('Shader fix for multiplayer pause menu not found! Missing ' + mp_pause_filename + '.')

else:
    with open('ShaderFixes/' + mp_pause_filename,'r+') as mp_pause_file:
        
        mp_pause_file.seek(1108) # number of bytes to line needing change
        mp_pause_file.write('  r0.x -= ' + str(delta_x) + ';')
        mp_pause_file.close()

if not os.path.exists('ShaderFixes/' + mp_map_filename):
    print('Shader fix for multiplayer minimap not found! Missing ' + mp_map_filename + '.')

else:
    with open('ShaderFixes/' + mp_map_filename,'r+') as mp_map_file:
        
        mp_map_file.seek(1108) # number of bytes to line needing change
        mp_map_file.write('  r0.x -= ' + str(delta_x) + ';')
        mp_map_file.close()


if not os.path.exists('ShaderFixes/' + subtitles_filename):
    print('Shader fix for subtitles not found! Missing ' + subtitles_filename + '.')

else:
    with open('ShaderFixes/' + subtitles_filename,'r+') as subtitles_file:
        
        subtitles_file.seek(1368) # number of bytes to line needing change
        subtitles_file.write('   o0.x+=' + str(delta_o) + ';')
        subtitles_file.close()

if not os.path.exists('Mods/' + subtitles_hud_checker):
    print('Fix for subtitles/HUD interaction not found! Missing ' + subtitles_hud_checker + '.')

# Disable shader hunting and enable Mods folder in config file.
print('Modifying d3dx.ini...')
with open('d3dx.ini','r+') as ini:
    
    ini_data = ini.read()
    ini.close()
    
ini_data = ini_data.replace(';include_recursive = Mods','include_recursive = Mods')
ini_data = ini_data.replace('hunting=1','hunting=0')
    
with open('d3dx.ini','w') as ini:
    
    ini.write(ini_data);
    ini.close()

wait = input('Script complete. Press any key to close.')
