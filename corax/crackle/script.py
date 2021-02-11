
from corax.crackle.condition import create_condition_checker
from corax.crackle.job import create_job


class CrackleScript:
    def __init__(self, name):
        self.name = name
        self.conditions = []
        self.actions = []
        self.theatre = None
        self.checkers = []

    def __str__(self):
        lines = self.conditions + self.actions
        return f"script {self.name}\n" + "\n".join(lines)

    def build(self):
        if self.theatre is None:
            msg = (
                "CrackleScript cant be built when attribute "
                f"{self.name}.theatre isn't set.")
            raise RuntimeError(msg)
        self.checkers = [
            create_condition_checker(line, self.theatre)
            for line in self.conditions]

    def jobs(self):
        return [create_job(line, self.theatre) for line in self.actions]

    def check(self):
        return all(checker() for checker in self.checkers)

