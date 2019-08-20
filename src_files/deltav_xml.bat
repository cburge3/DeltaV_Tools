@echo off
Utf16ToUtf8.exe ..\inputs\%1.fhx ..\inputs\%1_8.fhx
FhxToXml2005.exe ..\inputs\%1_8.fhx ..\inputs\%1.xml
del ..\inputs\%1_8.fhx
echo done