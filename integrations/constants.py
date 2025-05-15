from enum import Enum


class IntegrationName(Enum):
    FITBIT = "fitbit"

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]


class UserIntegrationStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]
