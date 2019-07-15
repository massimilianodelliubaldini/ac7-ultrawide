import sys, os, shutil, binascii, zipfile, ctypes, math, glob
from datetime import datetime

# Must be in game root folder.
if not os.path.isfile('Ace7Game.exe'):
    wait = input('Ace7Game.exe not found in this folder. Press any key to close...')
    sys.exit(0)

# Get resolution from OS.
u32 = ctypes.windll.user32
u32.SetProcessDPIAware()

[your_total_width, your_total_height] = [u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)]
your_aspect_ratio = your_total_width / your_total_height

# Game calculates positions as if your monitor was always 1080p. These values are useful for those calculations.
standard_monitor_height = 1080
standardized_monitor_width = your_total_width * (standard_monitor_height / your_total_height)

# Get confirmation from user.
print('Your screen size appears to be ' + str(your_total_width) + 'x' + str(your_total_height) + '.')
prompt = ''
while prompt.lower() != 'y':
    prompt = input('Is that correct? Y to continue, N to cancel:')

    if prompt.lower() == 'n':
        wait = input('Canceled. Press any key to close.')
        sys.exit(0)

# Determining FOV hex value.
# Math below is based on FOV equations found on Wikipedia. Aspect Ratio = tan(H/2) / tan(V/2)
# where H and V are the horizontal and vertical field of view angles respectively. 
# Horizontal FOV on a standard 16:9 monitor is normally 90 degrees.
# That gives us a value for V (~58.7 deg), which we will keep constant no matter the aspect ratio.
# We then solve for H given your new aspect ratio.
print('Determining FOV hex value...')
horizontal_fov_radians = 2 * math.atan(your_aspect_ratio * math.tan(math.atan(9/16))) # Shortcutting a lot of math here.
horizontal_fov_degrees = math.degrees(horizontal_fov_radians)
print('Horizontal FOV: ' + str(round(horizontal_fov_degrees, 1)) + ' degrees.')

# This is a linear approximation to turn degrees into a hex value - found experimentally, not mathematically.
# Point 1: x1 = 90, y1 = 981577 (in hex, 0E FA 35) (standard 16:9 monitor, stock value in game exe).
# Point 2: x2 = 106.7, y2 = 3145728 (in hex, 30 00 00) (3440x1440 monitor, and almost pixel-perfect matching Point 1).
decimal_value = round((129591 * horizontal_fov_degrees) - 10681633)

hex_value = format(decimal_value, '06X') # Pad for leading zeros.
hex_string = ' '.join(map(str.__add__, hex_value[-2::-2], hex_value[-1::-2])) # Reverse the string by byte and separate with spaces.
hex_string = hex_string + ' 3C D8 F5' # First 3 bytes actually determine FOV, last 3 bytes are explained below.
print('New FOV hex value: ' + str(hex_string))

# Back up the game exe.
print('Backing up the game exe...')
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

if not os.path.isfile('Ace7Game.exe_' + timestamp):
    shutil.copy2('Ace7Game.exe','Ace7Game.exe_' + timestamp)

# Edit the game exe.
print('Modifying the game exe...')
with open('Ace7Game.exe','rb+') as exe:

    exe_data = exe.read()
    exe.close()

# The value '41 2C 01 4C 89 CB 0F 29' is only found once in the EXE.
exe_data = exe_data.replace(bytes.fromhex('41 2C 01 4C 89 CB 0F 29'), bytes.fromhex('41 2C 00 4C 89 CB 0F 29')) # Removes black bars.

# '35 FA 0E' is the default FOV value we want to replace, but it is found several times in the EXE, and we only want to replace it once. 
# How do we know which one to replace? '3C D8 F5' happens to follow that value at the FOV address, and it doesn't follow any other addresses with the same value.
# So when we search for '35 FA 0E 3C D8 F5' we only find it once, which is exactly what we need.
exe_data = exe_data.replace(bytes.fromhex('35 FA 0E 3C D8 F5'), bytes.fromhex(hex_string)) # Fixes field of view.

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

if bytes_changed == 0:
    print('WARNING: No bytes were changed. Was the game already patched? Recommend restoring exe from backup and rerunning this script...')
elif bytes_changed > 4:
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
    wait = input('3Dmigoto zip file not found. Press any key to close.')
    sys.exit(0)

tdm_zip = tdm_list[0]
tdm_dir = tdm_zip[:tdm_zip.rfind('.')]

# Unpack 3Dmigoto.
print('Unpacking ' + tdm_zip + '...')
zip_ref = zipfile.ZipFile(tdm_zip, 'r')
zip_ref.extractall(tdm_dir)
zip_ref.close()

# Check for correct folder structure.
try:
    item_list = os.listdir(tdm_dir + '/x64')
except WinError:
    wait = input('Could not find ' + tdm_dir + '/x64 folder. Press any key to close.')
    sys.exit(0)

# Copy files from x64 folder to game root folder.
print('Installing 3Dmigoto...')
for item in item_list:
    
    tdm_item = tdm_dir + '/x64/' + item
    try:
        if not os.path.exists(item):
            print('Copying folder ' + item)
            shutil.copytree(tdm_item, item)
    except:
        if not os.path.exists(item):
            print('Copying file ' + item)
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

hud_shift_amount = (standardized_monitor_width - 1920) / 3840 # divide by 1920, then divide by 2.
hud_shift_amount = round(hud_shift_amount, 4)

subtitle_shift_amount = 1 - ((16/9) / your_aspect_ratio)
subtitle_shift_amount = round(subtitle_shift_amount, 4)

if not os.path.exists('ShaderFixes/' + hud_filename):
    print('WARNING: Shader fix for HUD not found! Missing ' + hud_filename + '.')

else:
    with open('ShaderFixes/' + hud_filename,'r+') as hud_file:
        
        hud_file.seek(769) # number of bytes to line needing change
        hud_file.write('  r1.x -= ' + str(hud_shift_amount) + ';')
        hud_file.close()

if not os.path.exists('ShaderFixes/' + map_filename):
    print('WARNING: Shader fix for minimap not found! Missing ' + map_filename + '.')

else:
    with open('ShaderFixes/' + map_filename,'r+') as map_file:
        
        map_file.seek(1035) # number of bytes to line needing change
        map_file.write('  r0.x -= ' + str(hud_shift_amount) + ';')
        map_file.close()

if not os.path.exists('ShaderFixes/' + char_filename):
    print('WARNING: Shader fix for character portraits not found! Missing ' + char_filename + '.')

else:
    with open('ShaderFixes/' + char_filename,'r+') as char_file:
        
        char_file.seek(1035) # number of bytes to line needing change
        char_file.write('  r0.x -= ' + str(hud_shift_amount) + ';')
        char_file.close()

if not os.path.exists('ShaderFixes/' + map_m7_filename):
    print('WARNING: Shader fix for glitchy minimap not found! Missing ' + map_m7_filename + '.')

else:
    with open('ShaderFixes/' + map_m7_filename,'r+') as map_m7_file:
        
        map_m7_file.seek(1038) # number of bytes to line needing change
        map_m7_file.write('  r1.x -= ' + str(hud_shift_amount) + ';')
        map_m7_file.close()

if not os.path.exists('ShaderFixes/' + char_m7_filename):
    print('WARNING: Shader fix for glitchy character portraits not found! Missing ' + char_m7_filename + '.')

else:
    with open('ShaderFixes/' + char_m7_filename,'r+') as char_m7_file:
        
        char_m7_file.seek(1038) # number of bytes to line needing change
        char_m7_file.write('  r1.x -= ' + str(hud_shift_amount) + ';')
        char_m7_file.close()


if not os.path.exists('ShaderFixes/' + mp_hud_filename):
    print('WARNING: Shader fix for multiplayer HUD not found! Missing ' + mp_hud_filename + '.')

else:
    with open('ShaderFixes/' + mp_hud_filename,'r+') as mp_hud_file:
        
        mp_hud_file.seek(769) # number of bytes to line needing change
        mp_hud_file.write('  r1.x -= ' + str(hud_shift_amount) + ';')
        mp_hud_file.close()


if not os.path.exists('ShaderFixes/' + mp_pause_filename):
    print('WARNING: Shader fix for multiplayer pause menu not found! Missing ' + mp_pause_filename + '.')

else:
    with open('ShaderFixes/' + mp_pause_filename,'r+') as mp_pause_file:
        
        mp_pause_file.seek(1108) # number of bytes to line needing change
        mp_pause_file.write('  r0.x -= ' + str(hud_shift_amount) + ';')
        mp_pause_file.close()

if not os.path.exists('ShaderFixes/' + mp_map_filename):
    print('WARNING: Shader fix for multiplayer minimap not found! Missing ' + mp_map_filename + '.')

else:
    with open('ShaderFixes/' + mp_map_filename,'r+') as mp_map_file:
        
        mp_map_file.seek(1108) # number of bytes to line needing change
        mp_map_file.write('  r0.x -= ' + str(hud_shift_amount) + ';')
        mp_map_file.close()


if not os.path.exists('ShaderFixes/' + subtitles_filename):
    print('WARNING: Shader fix for subtitles not found! Missing ' + subtitles_filename + '.')

else:
    with open('ShaderFixes/' + subtitles_filename,'r+') as subtitles_file:
        
        subtitles_file.seek(1368) # number of bytes to line needing change
        subtitles_file.write('   o0.x+=' + str(subtitle_shift_amount) + ';')
        subtitles_file.close()

if not os.path.exists('Mods/' + subtitles_hud_checker):
    print('WARNING: Fix for subtitles/HUD interaction not found! Missing ' + subtitles_hud_checker + '.')

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

wait = input('Script completed successfully. Press any key to close.')
