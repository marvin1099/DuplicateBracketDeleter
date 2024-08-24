# DuplicateBracketDeleter
Ever Saved a file as "FILENAME (1)" because "FILENAME" was used already.  
If yes this deletes and moves files to get rid of the brackets and parentheses.

## Dependencys
Download and Install:
- Python 

This is not needed if you use the compiled version

## Downloads
Downloads / Releases are here:  
https://codeberg.org/marvin1099/Bracket-Number-Deleter/releases
 
## Use
Keep in mind `delete-duplicates.py` will be the name of the file downloaded.  
This name is different if you use the copiled version.  
Its `delete-duplicates-windows.exe` for windows  
and `delete-duplicates-linux` for linux.  
Open the terminal / the console and run:
```
PATH/TO/delete-duplicates.py PATH/OF/DUPLICATES
```
Replace PATH/TO/ with the path of the delete-duplicates.py.  
Also relace PATH/OF/DUPLICATES with your path of duplicate files.  
After that a config will open where you can change what the script will do.  
Then open the terminal / the console and run:
```
PATH/TO/delete-duplicates.py
```
To run the run the commands listed in the action file.
The action file will do what the explanation says by default.
But you can change what it will do quite easily.
Just read the file it has all the needed info.

## Explanation
To better explain the default, let's consider:
- File (1).txt
- File (2).txt
- File (3).txt
- File.txt

Then it will delete the oldest 3 files,  
keep the newest and rename it to File.txt