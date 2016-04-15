@echo off
setlocal
set DTFOREVER=%DATE:.=-%@%TIME::=-%
set DTFOREVER=%DTFOREVER: =%
@echo export to directory %DTFOREVER%
for /f "tokens=1,2 delims= " %%e in (collections.txt) do (
  @echo export collection %%e
  "C:\Program Files\MongoDB\Server\3.2\bin\mongoexport" -h localhost:8001 -d cross -c %%e -o %DTFOREVER%/%%e.json -f %%f
  @echo OK!
)
pause