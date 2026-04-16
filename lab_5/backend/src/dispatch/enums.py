from enum import StrEnum


class FitnessLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MuscleGroup(StrEnum):
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    FOREARMS = "forearms"
    QUADRICEPS = "quadriceps"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    ABS = "abs"
    OBLIQUES = "obliques"


class ExerciseCategory(StrEnum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    STRETCHING = "stretching"
    PLYOMETRICS = "plyometrics"


class Equipment(StrEnum):
    BARBELL = "barbell"
    DUMBBELL = "dumbbell"
    BODYWEIGHT = "bodyweight"
    MACHINE = "machine"
    CABLE = "cable"
    BAND = "band"
    KETTLEBELL = "kettlebell"
    OTHER = "other"


class SessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SplitType(StrEnum):
    FULL_BODY = "full_body"
    UPPER_LOWER = "upper_lower"
    PUSH_PULL_LEGS = "push_pull_legs"
    CUSTOM = "custom"
