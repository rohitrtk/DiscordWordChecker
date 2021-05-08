import random

class ErrorMessageGenerator:
    def __init__(self, file_name):
        with open(file_name) as reader:
            self.messages = reader.readlines()

        self.messages = [line.strip() for line in self.messages]


    def get_random_message(self):
        return self.messages[random.randrange(len(self.messages))]