set count=%1
F:
FOR /l %%i IN (1, 1, %count%) DO start C:/Python27/python.exe Executor.py