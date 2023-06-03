from random import choice
from time import sleep

print("Welcome!")
print("Every 1 second I print a random message!")

while True:
    print(choice(["Hello World!", "Another random message", "What's your name? I'm Bob the builder.",
                  "So.. you like the messages so far?", "Dafna and Doodlidoo", "Bond, James bond.",
                  "wait 1 more seconds for the next message", "diffeomorphism", "My ideas are starting to run out",
                  "Sara sings a happy song", "What year is it?", "Feels like i'm talking to myself",
                  "So.. the messages of the executor to my left sucks don't they..", "I need some sleep."]))
    sleep(1)
