# Bracket-Number-Deleter
Ever Saved a file as "FILENAME (1)" because "FILENAME" was used already.  
If yes this deletes and moves files to get rid of the brackets

# Downloads
Downloads / Releases are Here:  
https://codeberg.org/marvin1099/Bracket-Number-Deleter/releases

# Explanation
To Beter Explain,        
if there is a:
- File (1).txt
- File (2).txt
- File (3).txt
- File.txt

If will delete:
- File (1).txt
- File (2).txt
- File.txt  
And renames "File (3).txt" to "File.txt".   

The highest number in brackets is assumed to be the newest file.      
It asks for the folder to search for and creates a log file.      
It has the option to simulate (it will ask), that will only create the log file and wont do anything with your file.      
The log file can be executed with Autohotkey if it is renamed and possibly needed.        
