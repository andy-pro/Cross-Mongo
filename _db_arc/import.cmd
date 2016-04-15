@echo off
if exist crosses.json (
  for %%c in (auth_user,auth_group,auth_membership,cables,crosses,verticals,plints) do (
    @echo import collection "%%c"
    "C:\Program Files\MongoDB\Server\3.2\bin\mongoimport" -h localhost:8001 -d cross --drop -c %%c --file %%c.json
    @echo OK!
  )
) else (
  @echo Put script into TIMESTAMP directory!
)
pause