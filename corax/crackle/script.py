import logging
from corax.crackle.condition import create_condition_checker
from corax.crackle.job import create_job


class CrackleScript:
    def __init__(self, name):
        self.name = name
        self.conditions = []
        self.actions = []
        self.checkers = []
        self.locals = {}

    def __repr__(self):
        conditions = "  " + "\n  ".join(self.conditions)
        actions = "    " + "\n    ".join(self.actions)
        return f"script {self.name}\n{conditions}\n{actions}\n\n"

    def build(self, theatre):
        self.checkers = [
            create_condition_checker(line, theatre)
            for line in self.conditions]

    def create_job(self, index, theatre):
        try:
            line = self.actions[index]
            return create_job(line, theatre, self)
        except Exception:
            print(f'Fail in script: {self.name} at action {index}: {line}')
            raise

    def check(self):
        checks = [checker() for checker in self.checkers]
        return all(checks)


class CrackleEvent:
    def __init__(self, name):
        self.name = name
        self.actions = []
        self.locals = {}

    def __repr__(self):
        actions = "  " + "\n  ".join(self.actions)
        return f"event {self.name}\n{actions}\n\n"

    def create_job(self, index, theatre):
        try:
            line = self.actions[index]
            return create_job(line, theatre, self)
        except Exception:
            print(f'Fail in script: {self.name} at action {index}: {line}')
            raise