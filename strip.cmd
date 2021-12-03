echo off
set filename=%1
strip-hints %1% --inplace --to-empty --strip-nl
