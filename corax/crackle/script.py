import logging
from corax.crackle.condition import create_condition_checker
from corax.crackle.job import create_job


class CrackleScript:
    def __init__(self, name):
        self.name = name
        self.conditions = []
        self.actions = []
        self.checkers = []

    def __str__(self):
        lines = self.conditions + self.actions
        return f"script {self.name}\n" + "\n".join(lines)

    def build(self, theatre):
        self.checkers = [
            create_condition_checker(line, theatre)
            for line in self.conditions]

    def jobs(self, theatre):
        return [create_job(line, theatre) for line in self.actions]

    def check(self):
        checks = [checker() for checker in self.checkers]
        message = self.name + ": " + str([str(r) + ": " + c for r, c in zip(checks, self.conditions)])
        logging.debug(message)
        return all(checks)

