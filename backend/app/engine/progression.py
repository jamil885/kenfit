"""Suggestions only; prescriptions and historical snapshots never change here."""


def suggest(log):
    grouped = {}
    for result in log.results:
        grouped.setdefault(result.position, []).append(result)
    suggestions = []
    for position, results in grouped.items():
        required_sets = results[0].prescribed_sets
        all_sets = required_sets is not None and {r.set_number for r in results} == set(
            range(1, required_sets + 1)
        )
        reps_met = all(
            r.prescribed_reps is not None and r.reps is not None and r.reps >= r.prescribed_reps
            for r in results
        )
        effort_known = all(r.rpe is not None and r.rpe <= 8 for r in results)
        loaded = all(r.weight_kg is not None and r.weight_kg > 0 for r in results)
        if log.status == "completed" and all_sets and reps_met and effort_known and loaded:
            action = "review_increase"
            load = round(min(r.weight_kg for r in results) * 1.025, 2)
        else:
            action = "repeat_and_review"
            load = None
        suggestions.append(
            {
                "position": position,
                "exercise_id": results[0].exercise_id,
                "action": action,
                "suggested_weight_kg": load,
                "notice": "Advisory only; confirm all prescribed sets, technique and recovery before applying.",
            }
        )
    return {"log_id": log.id, "suggestions": suggestions}
