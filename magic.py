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

# Download shader fix.
print('Downloading shader fixes...')
sf_url = 'https://gist.githubusercontent.com/martinsstuff/7ae3b02360478c72d2c696f5f96b8bb4/raw/4d8254987f23392c4f05a032f44f7583d90c4db6/9958a636cbef5557-ps_replace.txt'
sf_txt = sf_url[sf_url.rfind('/')+1:]
urllib.request.urlretrieve(sf_url, 'ShaderFixes/' + sf_txt)

# Modify shader fix for resolution width.
print('Modifying shader fixes for resolution...')
hud_x = (res_x - 1920) / 3840 # divide by 1920, then divide by 2.
hud_x = round(hud_x, 4)

with open('ShaderFixes/' + sf_txt,'r+') as sf:
    
    sf.seek(965) # number of bytes to r1.x
    sf.write('  r1.x -= ' + str(hud_x) + ';')

    sf.close()

wait = input('Script complete. Press any key to close.')
