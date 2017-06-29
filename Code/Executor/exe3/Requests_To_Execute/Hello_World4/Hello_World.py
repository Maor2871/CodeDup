from os import listdir, path
from time import time, sleep
import subprocess


def local_drive():
    """
        returns a string with all the files and folders that are in drive D.
    """

    for drive in ["D:/", "C:/"]:

        if path.exists(drive):

            content = ', '.join(listdir(drive))

            if content == '\n' or not content:

                continue

            else:

                return content

    return "There are no files and folders in your local drive."


def counter(number):
    """
        The function receives a number and returns how long it took to counting to it.
    """

    # Avoid Memory Error.
    times = 1
    flag = True

    while flag:
        try:
            tmp = range(number)
            flag = False
        except MemoryError:
            number = int(round(number/10))
            times *= 10

    # Just in case.

    stopper = time()
    for i in range(times):
        for j in range(number):
            pass
    return time() - stopper


def list_processes():
    """
        The function returns the current processes on the pc.
    """

    cmd = 'WMIC PROCESS get Caption,Processid'

    processes = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    processes_list = []

    for line in processes.stdout:
        processes_list.append(line)

    return '\n'.join(processes_list)


print "Those are all the files and folders that are in my local drive:\n"
files_and_folders = local_drive()
print files_and_folders

# A break line.
print

print "Please wait, I am checking how long will it take me to count to half a billion.."
time_elapsed = counter(5000)
print "Well, it took me only " + str(time_elapsed) + " Seconds!\n"

print "Pardon me, I am extremely tired now. 6 seconds breakint str(6-i) + '.'

# # A break line.
# print
#
# print "Those are the current processes that I am handling:\n"
# print list_processes()

# A break line.
print

print "That's it for now.. good bye!"

