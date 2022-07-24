import logging
from corax.crackle.condition import create_condition_checker
from corax.crackle.job import create_job


class CrackleScript:
    def __init__(self, name):
        self.name = name
        self.conditions = []
        self.actions = []
        self.checkers = []

    def __repr__(self):
        conditions = "  " + "\n  ".join(self.conditions)
        actions = "    " + "\n    ".join(self.actions)
        return f"script {self.name}\n{conditions}\n{actions}\n\n"

    def build(self, theatre):
        self.checkers = [
            create_condition_checker(line, theatre)
            for line in self.conditions]

    def jobs(self, theatre):
        return [create_job(line, theatre) for line in self.actions]

    def check(self):
        checks = [checker() for checker in self.checkers]
        return all(checks)


class CrackleEvent:
    def __init__(self, name):
        self.name = name
        self.actions = []

    def __repr__(self):
        actions = "  " + "\n  ".join(self.actions)
        return f"event {self.name}\n{actions}\n\n"

    def jobs(self, theatre):
        return [create_job(line, theatre) for line in self.actions]
