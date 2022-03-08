import random

class Random:
    bankId = random.randrange(100, 9999, 1)
    accountId = random.randrange(1000000, 9999999, 1)

    @staticmethod
    def get_bank():
        bankId = random.randrange(100, 9999, 1)
        return bankId

    @staticmethod
    def get_acount():
        accountId = random.randrange(1000000, 9999999, 1)
        return accountId











