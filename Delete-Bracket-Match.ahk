;/*
while (Folder = "") {
  FileSelectFile, Folder, Options, C:\Users\This-Folder.txt, Select Folder to Clean, Use-This-Folder
  if (Folder != "") {
    SplitPath, Folder ,, ActualFolder
    if not InStr(FileExist(ActualFolder), "D")
      Folder := ""
  }
  if (Folder = "")
    MsgBox,, Delete Useless, Use a existing Folder please, 5
}
;*/
Simulation := True
MsgBox, 4, Simulate,% "Simulate (Yes) or delete duplikats right away (No)", 10
IfMsgBox, No
  Simulation := False


FileDelete,%A_ScriptFullPath%-log.txt
FormatTime, Time,,yyyy.MM.dd HH:mm:ss
FileAppend,% ";INFO *This log can be run with Autohotkey by changing the exetention to .ahk if so nessesary (Autohotkey needs to be installed)`n;Log started for folder: " . ActualFolder . "\`n;Log started at: " . Time . "`n", %A_ScriptFullPath%-log.txt

;Teporeay folder for testing
;ActualFolder := "D:\Marvin\Documents\Autohotkey\Old Deletion"
Loop, Files, %ActualFolder%\*, DF
{
  Str := ""
  if StrLen(A_LoopFileExt) > 0
  {
    Fxle := SubStr(A_LoopFileName, 1, StrLen(A_LoopFileName)-StrLen(A_LoopFileExt)-1)
    Ext := "." . A_LoopFileExt
  }
  else
  {
    Fxle := A_LoopFileName
    Ext := ""
  }
  Fite := StrSplit(Fxle, A_Space)
  for i, v in Fite
  {
    if not (i = Fite.MaxIndex() or i = (Fite.MaxIndex() - 1))
      Str .= Fite[i] . " "
    else if (i != Fite.MaxIndex())
      Str .= Fite[i]
  }
  if (Str = "")
    {
    Str := Fite[1]
    }
  if (Fite.MaxIndex() > 1)
  {
    Ending := Fite[Fite.MaxIndex()]
    Num := StrSplit(Ending , A_Space, "()[]")
    Num := Num[1]
  }
  Dot := "."
  Dotet := StrSplit(Num, Dot)
  if not (SubStr(Ending, 0) = "]" or SubStr(Ending, 0) = ")")
    Num := "s"
  if ((Num is integer) and Num < 101 and Num != "!" and not (Dotet[2] != "" or Dotet[3] != ""))
    Idetifier := Num
  else
  {
    Idetifier := 0
    if (Ending != "")
    {
      Str .= " " . Ending
      Ending := ""
    }
  }
  Str .= Ext
  if (Filelist != "")
  {
    if (Filelist[1] = Str)
    	Filelist.Push(Str,Idetifier,A_LoopFileName)
    else
    {
      newv = -1
      newi = 2
      for i, v in Filelist
      {
        if (Mod(i,3) = 2)
          if (v > newv)
          {
            newv := v
            newi := i
          }
      }
      for i, v in Filelist
      {
        if (i != (newi+1))
          if (Mod(i,3) = 0)
          {
            ;Log Planed Deletion
            FileAppend,% "FileDelete, " . ActualFolder . "\" . v . "`n", %A_ScriptFullPath%-log.txt
            ;Ucoment Below to Delete File
            if (Simulation = False)
              FileDelete,% ActualFolder . "\" . v
          }
      }
      if (Filelist[(newi+1)] != Filelist[(newi-1)])
      {
        SourceFile := ActualFolder . "\" . Filelist[(newi+1)]
        DesFile := ActualFolder . "\" . Filelist[(newi-1)]
        ;Log Planed Filerenaming
        FileAppend,% "FileMove, " . SourceFile . ", " . DesFile . ", 1`n", %A_ScriptFullPath%-log.txt
        ;Ucoment Below to Rename File
        if (Simulation = False)
          FileMove,% SourceFile,% DesFile, 1
      }
      Filelist := [Str,Idetifier,A_LoopFileName]
    }
  }
  else
  	Filelist := [Str,Idetifier,A_LoopFileName]
}

newv = -1
newi = 2
for i, v in Filelist
{
  if (Mod(i,3) = 2)
    if (v > newv)
    {
      newv := v
      newi := i
    }
}
for i, v in Filelist
{
  if (i != (newi+1))
    if (Mod(i,3) = 0)
    {
      ;Log Planed Deletion
      FileAppend,% "FileDelete, " . ActualFolder . "\" . v . "`n", %A_ScriptFullPath%-log.txt
      ;Ucoment Below to Delete File
      FileDelete,% ActualFolder . "\" . v
    }
}
if (Filelist[(newi+1)] != Filelist[(newi-1)])
{
  SourceFile := ActualFolder . "\" . Filelist[(newi+1)]
  DesFile := ActualFolder . "\" . Filelist[(newi-1)]
  ;Log Planed Filerenaming
  FileAppend,% "FileMove, " . SourceFile . ", " . DesFile . ", 1`n", %A_ScriptFullPath%-log.txt
  ;Ucoment Below to Rename File
  FileMove,% SourceFile,% DesFile, 1
}
Filelist := ""
