import sys, os, shutil, binascii, urllib.request, zipfile, ctypes, math

# Must be in game root folder.
if not os.path.isfile('Ace7Game.exe'):
    wait = input('Ace7Game.exe not found in this folder. Press any key to close...')
    sys.exit(0)

# Get desired resolution from user.
fov_hex = ''
while fov_hex == '':
    print('Please select a resolution:')
    print('1: 2560x1080')
    print('2: 3440x1440')
    print('3: 32:9')
    print('4: 48:9')
    print('5: 16:9 (original)')
    res = input('')

    if res == '1':
        fov_hex = 'AA05333C'
    elif res == '2':
        fov_hex = 'EDD1333C'
    elif res == '3':
        fov_hex = 'FCCF653C'
    elif res == '4':
        fov_hex = '707B8B3C'
    elif res == '5':
        fov_hex = '35FA0E3C'
    else:
        print('Invalid selection.')

# Back up the game exe.
if not os.path.isfile('Ace7Game.exe_orig'):
    shutil.copy2('Ace7Game.exe','Ace7Game.exe_orig')

# Overwrite FOV value in game exe.
with open('Ace7Game.exe','rb+') as exe:

    exe.seek(int('0A03E32A', 16)) # address to remove black bars
    exe.write(binascii.a2b_hex('00'))

    exe.seek(int('02534658', 16)) # address of field of view
    exe.write(binascii.a2b_hex(fov_hex))
    
    exe.close()

# Download 3Dmigoto.
tdm_url = 'https://github.com/bo3b/3Dmigoto/releases/download/1.3.14/3Dmigoto-1.3.14.zip'
tdm_zip = tdm_url[tdm_url.rfind('/')+1:]
tdm_dir = tdm_zip[:tdm_zip.rfind('.')]

if not os.path.isfile(tdm_zip):
    urllib.request.urlretrieve(tdm_url, tdm_zip)

# Unpack 3Dmigoto.
zip_ref = zipfile.ZipFile(tdm_zip, 'r')
zip_ref.extractall(tdm_dir)
zip_ref.close()

os.remove(tdm_zip)

# Copy files from x64 folder to game root folder.
for item in os.listdir(tdm_dir + '/x64'):
    
    tdm_item = tdm_dir + '/x64/' + item
    try:
        if not os.path.exists(item):
            shutil.copytree(tdm_item, item)
    except:
        if not os.path.exists(item):
            shutil.copy2(tdm_item, item)

# Disable shader hunting in config file.
with open('d3dx.ini','r+') as ini:
    
    ini.seek(10202) # number of bytes to hunting
    ini.write('hunting=0')

    ini.close()

# Download shader fix.
sf_url = 'https://gist.githubusercontent.com/martinsstuff/7ae3b02360478c72d2c696f5f96b8bb4/raw/4d8254987f23392c4f05a032f44f7583d90c4db6/9958a636cbef5557-ps_replace.txt'
sf_txt = sf_url[sf_url.rfind('/')+1:]
urllib.request.urlretrieve(sf_url, 'ShaderFixes/' + sf_txt)

# Modify shader fix for resolution width.
u32 = ctypes.windll.user32
u32.SetProcessDPIAware()

[res_w, res_h] = [u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)]
res_w = res_w * (1080 / res_h)
res_x = (res_w - 1920) / 3840 # (x/1920)/2 = x/3840
res_x = round(res_x, 4)

with open('ShaderFixes/' + sf_txt,'r+') as sf:
    
    sf.seek(965) # number of bytes to r1.x
    sf.write('  r1.x -= ' + str(res_x) + ';')

    sf.close()

wait = input('Press any key to close...')
