@echo off
Utf16ToUtf8.exe %1.fhx %1_8.fhx
FhxToXml2005.exe %1_8.fhx %1.xml
del %1_8.fhx
echo done