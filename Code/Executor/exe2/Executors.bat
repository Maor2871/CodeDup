set count=%1
F:
cd Project\Code\
FOR /l %%i IN (1, 1, %count%) DO start python Executor.py