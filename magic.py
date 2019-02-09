import sys, os, shutil, binascii, urllib.request, zipfile, linecache

# Get desired resolution from user.
res_hex = ''
while res_hex == '':
    print('Please select a resolution:')
    print('1: 2560x1080')
    print('2: 3440x1440')
    print('3: 32:9')
    print('4: 48:9')
    print('5: 16:9 (original)')
    res = input('')

    if res == '1':
        res_hex = 'AA05333C'
    elif res == '2':
        res_hex = 'EDD1333C'
    elif res == '3':
        res_hex = 'FCCF653C'
    elif res == '4':
        res_hex = '707B8B3C'
    elif res == '5':
        res_hex = '35FA0E3C'
    else:
        print('Invalid selection.')

# Back up the game exe.
if not os.path.isfile('Ace7Game.exe_orig'):
    shutil.copy2('Ace7Game.exe','Ace7Game.exe_orig')

# Overwrite resolution values in game exe.
with open('Ace7Game.exe','rb+') as exe:

    exe.seek(int('0A03E32A', 16)) # address to remove black bars
    exe.write(binascii.a2b_hex('00'))

    exe.seek(int('03763968', 16)) # address of resolution
    exe.write(binascii.a2b_hex(res_hex))
    
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
sf_url = 'https://gist.githubusercontent.com/martinsstuff/7ae3b02360478c72d2c696f5f96b8bb4/raw/e7b421b718c34e36b504c0612d2df5d440e3b27a/9958a636cbef5557-ps_replace.txt'
sf_txt = sf_url[sf_url.rfind('/')+1:]

if not os.path.isfile(sf_txt):
    urllib.request.urlretrieve(sf_url, 'ShaderFixes/' + sf_txt)



wait = input('Press any key to close...')
