# ac7-ultrawide
Mod AC7 to work at ultrawide resolutions.

What it does:

1. Determines the resolution of the user's monitor(s).
2. Creates a time-stamped backup of the game executable. This is NOT for redistribution!
3. Hex edits the game executable to remove letterboxing (black side bars) and adjust the field of view (FOV).
4. Compares the modified exe against the backup to determine successful hex editing.
5. Unpacks 3Dmigoto into the game directory.
6. Modifies the shader files for the correct position and resolution.

WARNING: 

Due to the fact that this mod makes direct modification to the game executable, 
the game's new anticheat system may flag you and get you permanently banned from online play. 
This developer holds no responsibility if this happens to you! 

Prerequisites:

1. [Python 3.5 or newer](https://www.python.org/downloads/) (Make sure you allow it to modify your Windows PATH environment variable upon installation)
2. [3Dmigoto 1.3.16 or newer](https://github.com/bo3b/3Dmigoto/releases/) (You just need "3Dmigoto-1.3.\*.zip")

    **Warning:** The order of releases on the 3Dmigoto page is not completely chronological due to the way the file names are sorted, ensure that you are downloading the latest version by file name, not order in the list.

3. [Steamless](https://github.com/atom0s/Steamless) 
Installation: 

1. Download a zip file of 3Dmigoto and save it to \<Steam Installation Location\>\SteamApps\common\ACE COMBAT 7.
2. Clone this repository to, or download a zip and unpack it in, \<Steam Installation Location\>\SteamApps\common\ACE COMBAT 7.
3. Place Steamless wherever you want
4. Open Steamless.exe select Ace7Game.exe and click unpack file
5. Backup old Ace7Game.exe and rename the unpacked exe to Ace7Game.exe
6. Double magic.py click to run.

Uninstallation:

1. Delete d3d11.dll from your game directory.
2. Delete Ace7Game.exe from your game directory.
3. "Verify integrity of game files" in Steam. This will re-download the most up-to-date executable.

TODO:

1. Continue using most-up-to-date shader fixes.
2. Make install script more robust with user feedback.
3. Make installation less complex.
4. Improve code reuse.


