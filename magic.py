import sys, os, shutil, binascii, zipfile, ctypes, math, glob, time
from datetime import datetime

# Sets it to the correct directory, it wants to do system32 for me every time - Hydraxon
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

# Must be in game root folder.
if not os.path.isfile('Ace7Game.exe'):
    wait = input('ERROR: Ace7Game.exe not found in this folder. Press any key to close...')
    sys.exit(0)

# Add warning about the risk of getting flagged by anticheat.
print('WARNING: This mod may be flagged as a cheating tool by the new Ace Combat 7 anti-cheat system going live in August 2019.')
print('This developer holds no responsibility if this mod results in an online ban.')
prompt = ''
while prompt.lower() != 'y':
    prompt = input('Are you sure you wish to continue? Y to continue, N to cancel:')

    if prompt.lower() == 'n':
        wait = input('Canceled. Press any key to close.')
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
horizontal_fov_radians = 2 * math.atan(your_aspect_ratio * (9/16)) # Shortcutting a lot of math here.

# Word of warning: you can set this variable to a value of your choosing, e.g. 120,
# but do not play online with anything other than the automatically determined FOV. 
horizontal_fov_degrees = math.degrees(horizontal_fov_radians) 

print('Horizontal FOV: ' + str(round(horizontal_fov_degrees, 1)) + ' degrees.')

# This is a linear approximation to turn degrees into a hex value - found experimentally, not mathematically.
# Point 1: x1 = 90, y1 = 981557 (in hex, 0E FA 35) (standard 16:9 monitor, stock value in game exe).
# Point 2: x2 = 106.7, y2 = 3145728 (in hex, 30 00 00) (3440x1440 monitor, and almost pixel-perfect matching Point 1).
decimal_value = round((129591 * horizontal_fov_degrees) - 10681633)

hex_value = format(decimal_value, '06X') # Pad for leading zeros.
hex_string = ' '.join(map(str.__add__, hex_value[-2::-2], hex_value[-1::-2])) # Reverse the string by byte and separate with spaces.
hex_string = hex_string + ' 3C D8 F5' # First 3 bytes actually determine FOV, last 3 bytes are explained below.
print('New FOV hex value: ' + str(hex_string))

# Back up the game exe.
print('Backing up the game exe...')
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

attempts = 5
while attempts >= 0:
    try:
        if not os.path.isfile('Ace7Game.exe_' + timestamp):
            shutil.copy2('Ace7Game.exe','Ace7Game.exe_' + timestamp)

            # If we reach the break, then we hit no exceptions and we can safely leave the while loop.
            break

    except OSError as e:
        print('OSError ' + str(e.errno) + '. File may be locked by another process.')
        if attempts > 0:
            print('Will wait 5 seconds and try again. Attempts remaining: ' + str(attempts) + '.')
            time.sleep(5)
        else:
            wait = input('ERROR: Unable to backup game exe. Press any key to close.')
            sys.exit(0)
    finally:
        attempts -= 1

# Edit the game exe.
print('Modifying the game exe...')

attempts = 5
while attempts >= 0:
    try:
        with open('Ace7Game.exe','rb+') as exe:

            exe_data = exe.read()

            # If we reach the break, then we hit no exceptions and we can safely leave the while loop.
            break

    except OSError as e:
        print('OSError ' + str(e.errno) + '. File may be locked by another process.')
        if attempts > 0:
            print('Will wait 5 seconds and try again. Attempts remaining: ' + str(attempts) + '.')
            time.sleep(5)
        else:
            wait = input('ERROR: Unable to read game exe. Press any key to close.')
            sys.exit(0)
    finally:
        attempts -= 1

# The value '48 81 EC D0 00 00 00 F6 41 2C 01' is only found once in the EXE.
exe_data = exe_data.replace(bytes.fromhex('48 81 EC D0 00 00 00 F6 41 2C 01'), bytes.fromhex('48 81 EC D0 00 00 00 F6 41 2C 00')) # Removes black bars.

# '35 FA 0E' is the default FOV value we want to replace, but it is found several times in the EXE, and we only want to replace it once. 
# How do we know which one to replace? '3C D8 F5' happens to follow that value at the FOV address, and it doesn't follow any other addresses with the same value.
# So when we search for '35 FA 0E 3C D8 F5' we only find it once, which is exactly what we need.
exe_data = exe_data.replace(bytes.fromhex('35 FA 0E 3C D8 F5'), bytes.fromhex(hex_string)) # Fixes field of view.

attempts = 5
while attempts >= 0:
    try:
        with open('Ace7Game.exe','wb') as exe:

            exe.write(exe_data);

            # If we reach the break, then we hit no exceptions and we can safely leave the while loop.
            break

    except OSError as e:
        print('OSError ' + str(e.errno) + '. File may be locked by another process.')
        if attempts > 0:
            print('Will wait 5 seconds and try again. Attempts remaining: ' + str(attempts) + '.')
            time.sleep(5)
        else:
            wait = input('ERROR: Unable to rewrite game exe. Press any key to close.')
            sys.exit(0)
    finally:
        attempts -= 1

# Check to make sure nothing broke by comparing number of bytes modified. Should only be 4.
print('Verifying the game exe...')

attempts = 5
while attempts >= 0:
    try:
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

        if bytes_changed == 0:
            print('WARNING: No bytes were changed. Was the game already patched? Recommend restoring exe from backup and rerunning this script...')
        elif bytes_changed > 4:
            print('WARNING: More bytes were changed than expected! Recommend restoring exe from backup and performing those changes manually...')
        elif bytes_changed < 4:
            print('WARNING: Fewer bytes were changed than expected! Recommend restoring exe from backup and performing those changes manually...')
        else:
            print('Verification successful.')

        # If we reach the break, then we hit no exceptions and we can safely leave the while loop.
        break

    except OSError as e:
        print('OSError ' + str(e.errno) + '. File may be locked by another process.')
        if attempts > 0:
            print('Will wait 5 seconds and try again. Attempts remaining: ' + str(attempts) + '.')
            time.sleep(5)
        else:
            wait = input('ERROR: Unable to verify game exe. Press any key to close.')
            sys.exit(0)
    finally:
        attempts -= 1

# Check for 3Dmigoto zip file.
print('Checking for 3Dmigoto zip file...')
tdm_regex = '3Dmigoto-*.zip'
tdm_list = glob.glob(tdm_regex)

if not tdm_list:
    wait = input('ERROR: 3Dmigoto zip file not found. Press any key to close.')
    sys.exit(0)

# We want to make sure the version is >= 1.3.16. 
# Regex performance is better for subtitle handling in that version.
tdm_zip = None
for t in tdm_list:
    version_numbers = t[t.find('-') + 1 : t.rfind('.')]
    version_numbers = version_numbers.split('.')

    if  int(version_numbers[0]) >= 1 and \
        int(version_numbers[1]) >= 3 and \
        int(version_numbers[2]) >= 16:

        tdm_zip = t
        break

if tdm_zip is None:
    wait = input('ERROR: 3Dmigoto zip version must be >= 1.3.16. Press any key to close.')
    sys.exit(0)

tdm_dir = tdm_zip[:tdm_zip.rfind('.')]

# Unpack 3Dmigoto.
print('Unpacking ' + tdm_zip + '...')
zip_ref = zipfile.ZipFile(tdm_zip, 'r')
zip_ref.extractall(tdm_dir)
zip_ref.close()

# Check for correct folder structure.
try:
    item_list = os.listdir(tdm_dir + '/x64')
except OSError:
    wait = input('ERROR: Could not find ' + tdm_dir + '/x64 folder. Press any key to close.')
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
subtitles_filename = 'da86a094e768f000-vs_replace.txt'
hudfix_filename = 'hudtextfix.ini'

# Find and modify HUD location.
print('Modifying HUD and subtitles location...')

hud_shift_amount = (standardized_monitor_width - 1920) / 3840 # divide by 1920, then divide by 2.
hud_shift_amount = round(hud_shift_amount, 4) * -1

subtitle_shift_amount = 1 - ((16/9) / your_aspect_ratio)
subtitle_shift_amount = round(subtitle_shift_amount, 4) 

if not os.path.exists('ShaderFixes/' + subtitles_filename):
    print('WARNING: Shader fix for subtitles not found! Missing ' + subtitles_filename + '.')

else:
    with open('ShaderFixes/' + subtitles_filename,'r+') as subtitles_file:
        
        subtitles_file.seek(1368) # number of bytes to line needing change - TODO: This really needs to be more robust.
        subtitles_file.write('   o0.x+=' + str(subtitle_shift_amount) + ';')
        subtitles_file.close()

if not os.path.exists('Mods/' + hudfix_filename):
    print('WARNING: Fix for HUD and subtitles not found! Missing ' + hudfix_filename + '.')

else:
    with open('Mods/' + hudfix_filename, 'r+') as hudfix_ini:

        hudfix_ini_data = hudfix_ini.read()
        hudfix_ini.close()

    hudfix_ini_data = hudfix_ini_data.replace('l(-0.0000)', 'l(' + str(hud_shift_amount) + ')')

    with open('Mods/' + hudfix_filename, 'w') as hudfix_ini:
    
        hudfix_ini.write(hudfix_ini_data);
        hudfix_ini.close()

# Disable shader hunting and enable Mods folder in config file.
print('Modifying config file...')

if not os.path.exists('d3dx.ini'):
    print('WARNING: d3dx.ini config file not found!')

else:
    with open('d3dx.ini', 'r+') as config_ini:
        
        config_ini_data = config_ini.read()
        config_ini.close()
        
    config_ini_data = config_ini_data.replace(';include_recursive = Mods','include_recursive = Mods')
    config_ini_data = config_ini_data.replace('hunting=1','hunting=0')
        
    with open('d3dx.ini', 'w') as config_ini:
        
        config_ini.write(config_ini_data);
        config_ini.close()

wait = input('Script completed successfully. Press any key to close.')
