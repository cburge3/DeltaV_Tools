@echo off
Utf16ToUtf8.exe "..\%~2\%1.fhx" "..\%~2\%1_8.fhx"
FhxToXml2005.exe "..\%~2\%1_8.fhx" "..\%~2\%1.xml"
del "..\%~2\%1_8.fhx"
echo done