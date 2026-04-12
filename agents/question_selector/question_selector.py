# import json
# import random
# from collections import defaultdict


# # -----------------------------------
# # LOAD QUESTION BANK
# # -----------------------------------

# with open("qns.json", "r") as f:
#     question_bank = json.load(f)


# # -----------------------------------
# # SESSION STATE (per interview)
# # -----------------------------------

# TOPIC_LIMIT = 3

# session_state = {
#     "topic_count": defaultdict(int),
#     "previous_topic": None,
#     "questions_asked": set()
# }


# # -----------------------------------
# # FILTER QUESTIONS BY DIFFICULTY
# # -----------------------------------

# def filter_by_difficulty(difficulty):

#     candidates = []

#     for q in question_bank:
#         if q["difficulty"] == difficulty:
#             candidates.append(q)

#     return candidates


# # -----------------------------------
# # FILTER VALID TOPICS
# # -----------------------------------

# def get_valid_topics(questions):

#     valid_topics = set()

#     for q in questions:

#         topic = q["topic"]

#         if session_state["topic_count"][topic] >= TOPIC_LIMIT:
#             continue

#         if topic == session_state["previous_topic"]:
#             continue

#         valid_topics.add(topic)

#     return list(valid_topics)


# # -----------------------------------
# # SELECT LEAST ASKED TOPIC
# # -----------------------------------

# def select_topic(valid_topics):

#     if not valid_topics:
#         return None

#     min_count = min(
#         session_state["topic_count"][t]
#         for t in valid_topics
#     )

#     candidate_topics = [
#         t for t in valid_topics
#         if session_state["topic_count"][t] == min_count
#     ]

#     return random.choice(candidate_topics)


# # -----------------------------------
# # SELECT QUESTION FROM TOPIC
# # -----------------------------------

# def select_question_from_topic(topic, difficulty):

#     candidates = []

#     for q in question_bank:

#         if q["topic"] != topic:
#             continue

#         if q["difficulty"] != difficulty:
#             continue

#         if q["qid"] in session_state["questions_asked"]:
#             continue

#         candidates.append(q)

#     if not candidates:
#         return None

#     return random.choice(candidates)


# # -----------------------------------
# # MAIN SELECTOR FUNCTION
# # -----------------------------------

# def select_next_question(difficulty):
#     """
#     Input:
#         difficulty (float) -> from RL agent

#     Output:
#         question_json -> sent to orchestrator agent
#     """
#     pr

#     # Step 1: difficulty filter
#     diff_questions = filter_by_difficulty(difficulty)

#     # Step 2: topic filtering
#     valid_topics = get_valid_topics(diff_questions)

#     if not valid_topics:
#         return None

#     # Step 3: select topic
#     topic = select_topic(valid_topics)

#     # Step 4: select question
#     question = select_question_from_topic(topic, difficulty)

#     if question is None:
#         return None

#     # Step 5: update session state
#     session_state["topic_count"][topic] += 1
#     session_state["previous_topic"] = topic
#     session_state["questions_asked"].add(question["qid"])

#     # Step 6: return question JSON to orchestrator
#     return question



import json
import os
import random
from collections import defaultdict


# -----------------------------------
# LOAD QUESTION BANK
# -----------------------------------

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(MODULE_DIR)

QUESTION_BANK_PATHS = [
    os.path.join(MODULE_DIR, "qns.json"),
    os.path.join(ROOT_DIR, "Evaluator", "qns.json"),
]

for _candidate in QUESTION_BANK_PATHS:
    if os.path.exists(_candidate):
        with open(_candidate, "r") as f:
            question_bank = json.load(f)
        break
else:
    raise FileNotFoundError(
        "Could not locate qns.json. Checked: " + ", ".join(QUESTION_BANK_PATHS)
    )


# -----------------------------------
# SESSION STATE
# -----------------------------------

TOPIC_LIMIT = 3

session_state = {
    "topic_count": defaultdict(int),
    "previous_topic": None,
    "questions_asked": set()
}


def reset_session_state():

    session_state["topic_count"] = defaultdict(int)
    session_state["previous_topic"] = None
    session_state["questions_asked"] = set()


AVAILABLE_DIFFICULTIES = sorted({float(q["difficulty"]) for q in question_bank})


def nearest_difficulty(target_difficulty):

    if not AVAILABLE_DIFFICULTIES:
        return float(target_difficulty)

    target = float(target_difficulty)

    return min(AVAILABLE_DIFFICULTIES, key=lambda d: abs(d - target))


# -----------------------------------
# FILTER QUESTIONS BY DIFFICULTY
# -----------------------------------

def filter_by_difficulty(difficulty):

    candidates = []

    for q in question_bank:
        if q["difficulty"] == difficulty:
            candidates.append(q)

    return candidates


# -----------------------------------
# FILTER VALID TOPICS
# -----------------------------------

def get_valid_topics(questions):

    valid_topics = set()

    for q in questions:

        topic = q["topic"]

        if session_state["topic_count"][topic] >= TOPIC_LIMIT:
            continue

        if topic == session_state["previous_topic"]:
            continue

        valid_topics.add(topic)

    return list(valid_topics)


# -----------------------------------
# SELECT LEAST ASKED TOPIC
# -----------------------------------

def select_topic(valid_topics):

    if not valid_topics:
        return None

    min_count = min(
        session_state["topic_count"][t]
        for t in valid_topics
    )

    candidate_topics = [
        t for t in valid_topics
        if session_state["topic_count"][t] == min_count
    ]

    return random.choice(candidate_topics)


# -----------------------------------
# SELECT QUESTION FROM TOPIC
# -----------------------------------

def select_question_from_topic(topic, difficulty):

    candidates = []

    for q in question_bank:

        if q["topic"] != topic:
            continue

        if q["difficulty"] != difficulty:
            continue

        if q["qid"] in session_state["questions_asked"]:
            continue

        candidates.append(q)

    if not candidates:
        return None

    return random.choice(candidates)


# -----------------------------------
# MAIN SELECTOR FUNCTION
# -----------------------------------

def select_next_question(difficulty):

    target_difficulty = nearest_difficulty(difficulty)

    # Step 1: difficulty filter
    diff_questions = filter_by_difficulty(target_difficulty)

    # Step 2: topic filtering
    valid_topics = get_valid_topics(diff_questions)

    if not valid_topics:
        return None

    # Step 3: topic selection
    topic = select_topic(valid_topics)

    # Step 4: question selection
    question = select_question_from_topic(topic, target_difficulty)

    if question is None:
        return None

    # Step 5: update session state
    session_state["topic_count"][topic] += 1
    session_state["previous_topic"] = topic
    session_state["questions_asked"].add(question["qid"])

    return question


# -----------------------------------
# TEMPORARY CMD TEST (RL placeholder)
# -----------------------------------

if __name__ == "__main__":

    while True:

        difficulty = input("\nEnter difficulty (0.2 easy / 0.4 medium / 0.7 hard) or 'exit': ")

        if difficulty == "exit":
            break

        difficulty = float(difficulty)

        question = select_next_question(difficulty)

        if question is None:
            print("No question available.")
            continue

        print("\nSelected Question JSON")
        print("------------------------")
        print(question)