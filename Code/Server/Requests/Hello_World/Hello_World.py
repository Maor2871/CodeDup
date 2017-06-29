from os import listdir, path
#from time import time, sleep
import subprocess
from random import choice


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


# def counter(number):
#     """
#         The function receives a number and returns how long it took to counting to it.
#     """
#
#     # Avoid Memory Error.
#     times = 1
#     flag = True
#
#     while flag:
#         try:
#             tmp = range(number)
#             flag = False
#         except MemoryError:
#             number = int(round(number/10)case.
#     number = int(round(number/10))
#     times *= 10
#
#     stopper = time()
#     for i in range(times):
#         for j in range(number):
#             pass
#     return time() - stopper


def list_processes():
    """
        The function returns the current processes on the pc.
    """

    cmd = 'WMIC PROCESS get Caption'

    processes = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    processes_list = []

    for line in processes.stdout:
        processes_list.append(line)

    processes_list = [proc.replace("\r\r\n", "") for proc in processes_list]
    processes_list = [proc.replace(" ", "") for proc in processes_list]

    return ', '.join(processes_list[2:])

print "I am going to random weather I will raise an exception or not.. (33 %)"
i = choice([1, 2, 3])

if i == 2:

    raise Exception('Oh, no luck for me :S')

print "I'm good.. I'm good.\n"
are in my local drive:"
files_and_folders = local_drive()
print files_and_folders

# A break line.
print

# print "Please wait, I am checking how long will it take me to count to half a billion.."
# time_elapsed = counter(5000)
# print "Well, it took me only " + str(time_elapsed) + " Seconds!\n"
#
# print "Pardon me, I am extremely tired now. 6 seconds break will do."
# for i in range(6):
#     sleep(1)
#     print str(6-i) + '.'

# # A break line.
# print
#
print "Those are the current processes that I am handling:"
print list_processes()

# A break line.
print

print "That's it for now.. good bye!"

