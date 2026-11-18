import random
import re
from collections import defaultdict

ALLOWED = {
    "easy_medium": {"easy", "medium"},
    "medium_hard": {"medium", "hard"},
    "hard_extreme": {"hard", "extreme"},
    "custom": {"easy", "medium", "hard", "extreme"}
}

def key(text):
    return re.sub(r"\W+", " ", str(text or "").lower()).strip()

def validate(req):
    count = sum(s.count for s in req.sections)
    marks = sum(s.count * s.marks_each for s in req.sections)
    if not req.sections:
        raise ValueError("Configure at least one section.")
    if marks != req.max_marks:
        raise ValueError(f"Section marks add up to {marks}, not {req.max_marks}.")
    if req.topics and abs(sum(t.percentage for t in req.topics) - 100) > 0.01:
        raise ValueError("Topic percentages must total 100%.")
    if req.difficulty == "custom" and req.custom_easy + req.custom_medium + req.custom_hard != 100:
        raise ValueError("Custom difficulty percentages must total 100%.")
    return count

def create_sets(pool, req):
    total = validate(req)
    output, used_across_sets = [], set()
    for set_no in range(req.number_of_sets):
        rng = random.Random(2026 + set_no)
        allowed = ALLOWED[req.difficulty]
        candidates = [q for q in pool if q.get("difficulty", "medium") in allowed]
        if req.difficulty == "custom":
            candidates = list(pool)
        rng.shuffle(candidates)
        used, topic_counts, sections = set(), defaultdict(int), []
        topic_targets = {key(t.name): t.percentage for t in req.topics}
        for section in req.sections:
            types = ["mcq"] if section.question_type == "mcq" else ["descriptive"] if section.question_type == "descriptive" else ["mcq", "descriptive"]
            choices = [q for q in candidates if q.get("type") in types]
            chosen = []
            for _ in range(section.count):
                ranked = []
                for q in choices:
                    qkey = key(q.get("question"))
                    if not qkey or qkey in used:
                        continue
                    if q.get("suggested_marks") and int(q["suggested_marks"]) != section.marks_each:
                        continue
                    topic = key(q.get("topic"))
                    penalty = topic_counts[topic] * 3
                    if qkey in used_across_sets:
                        penalty += 8
                    target = topic_targets.get(topic)
                    if target is not None:
                        target_count = max(1, round(total * target / 100))
                        penalty += max(0, topic_counts[topic] - target_count) * 3
                    ranked.append((penalty + rng.random(), q))
                if not ranked:
                    raise ValueError(f"Insufficient eligible questions for {section.name}. Generate a larger question pool or relax constraints.")
                q = min(ranked, key=lambda x: x[0])[1]
                chosen.append({**q, "section": section.name, "marks": section.marks_each})
                qkey = key(q.get("question"))
                used.add(qkey)
                topic_counts[key(q.get("topic"))] += 1
                choices.remove(q)
            sections.append({"name": section.name, "questions": chosen})
        output.append({"set_name": chr(65 + set_no), "sections": sections})
        used_across_sets.update(used)
    return output
