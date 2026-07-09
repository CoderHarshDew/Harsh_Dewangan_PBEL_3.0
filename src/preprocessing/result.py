

class SchemaResult:

    def __init__(self):

        self.invalid = dict()
        self.nan_count = 0
        self.negative_count = 0
        self.inf_count = 0
        self.out_of_range_count = 0

    def __str__(self):
        return f"-----------------\nNan:  {self.nan_count})\nInf:  {self.inf_count}\nNegative:  {self.negative_count}\nOut of range values:  {self.out_of_range_count}\n-----------------\nNOTE: These are number of cell values not rows."


class RuleResult:

    def __init__(self):

        self.violators = dict()
        self.violator_counts = dict()

    def __str__(self):
        res = ""
        for rule in  self.violators:
            res += f"{rule}: {self.violator_counts[rule]}\n"

        return res

if __name__ == "__main__":
    pass