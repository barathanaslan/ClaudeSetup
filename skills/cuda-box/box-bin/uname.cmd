@echo off
rem Shim seen only by cmd/PowerShell (bash never resolves .cmd, so Git Bash keeps the real uname).
rem VS Code Remote-SSH probes "uname -rsv" and treats only msys/cygwin/windows32 as Windows;
rem Git's uname.exe answers MINGW64_NT, which it does not recognise, and the connection hangs.
echo MSYS_NT-10.0 windows32 (uname.cmd shim; real uname: "C:\Program Files\Git\usr\bin\uname.exe")
