from enum import Enum


class IntegrationName(Enum):
    Fitbit = "fitbit"
    Strava = "strava"

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
