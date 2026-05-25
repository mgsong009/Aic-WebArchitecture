import math
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional


def default_advanced_statistics() -> Dict[str, Any]:
    return {
        "clusters": [],
        "strategies": _empty_strategies(),
        "effort_samples": [],
        "effort_correlation": None,
        "topic_oi_samples": [],
        "similarity_bands": _empty_similarity_bands(),
        "difficulty_adjusted_aic": {
            "overall_mean_aic": None,
            "summary": [],
            "students": [],
            "method_note": "Mean-shift adjusted AIC with assignment z-score and percentile rank.",
        },
        "confidence_intervals": [],
        "anomaly_detection": {
            "items": [],
            "summary_counts": {"total": 0, "high": 0, "caution": 0, "low": 0},
            "rule_counts": [],
            "method_note": "해석 주의 신호이며 조작을 단정하지 않습니다.",
        },
    }


def build_advanced_statistics(rows) -> Dict[str, Any]:
    records = [_record_from_row(row) for row in rows]
    records = [record for record in records if record["aic_score"] is not None]
    if not records:
        return default_advanced_statistics()

    assignment_groups = defaultdict(list)
    for record in records:
        assignment_groups[record["assignment_id"]].append(record)

    overall_scores = [record["aic_score"] for record in records]
    overall_mean = _mean(overall_scores)

    summary = []
    students = []
    z_by_key = {}
    for assignment_id in sorted(assignment_groups):
        group = assignment_groups[assignment_id]
        scores = [record["aic_score"] for record in group]
        assignment_mean = _mean(scores)
        assignment_std = _sample_std(scores)
        offset = overall_mean - assignment_mean
        percentiles = _percentile_ranks(scores)
        reliability_label = "unstable" if len(group) < 5 else "stable"

        summary.append({
            "assignment_id": assignment_id,
            "assignment_title": group[0]["assignment_title"],
            "assignment_mean_aic": _round(assignment_mean),
            "assignment_std_aic": _round(assignment_std),
            "overall_mean_aic": _round(overall_mean),
            "difficulty_label": _difficulty_label(offset),
            "adjustment_offset": _round(offset),
            "n": len(group),
            "reliability_label": reliability_label,
            "method_note": _assignment_method_note(len(group)),
            "interpretation": _difficulty_interpretation(offset),
        })

        for record in sorted(group, key=lambda item: (item["student_name"], item["student_id"])):
            raw_aic = record["aic_score"]
            adjusted_aic = _clamp(raw_aic + offset)
            assignment_z = None if assignment_std in (None, 0) else (raw_aic - assignment_mean) / assignment_std
            percentile_rank = percentiles[raw_aic]
            z_by_key[(record["student_id"], assignment_id)] = assignment_z
            students.append({
                "student_id": record["student_id"],
                "student_name": record["student_name"],
                "assignment_id": assignment_id,
                "raw_aic": _round(raw_aic),
                "adjusted_aic": _round(adjusted_aic),
                "assignment_z": _round(assignment_z, 2),
                "percentile_rank": _round(percentile_rank),
                "interpretation": _student_interpretation(percentile_rank, offset),
            })

    confidence_intervals = [_confidence_interval("overall", None, "전체 AIC", overall_scores)]
    for assignment_id in sorted(assignment_groups):
        group = assignment_groups[assignment_id]
        scores = [record["aic_score"] for record in group]
        confidence_intervals.append(_confidence_interval("assignment", assignment_id, group[0]["assignment_title"], scores))

    anomaly_items = _detect_anomalies(records, z_by_key)
    summary_counts = _anomaly_summary_counts(anomaly_items)
    rule_counts = _anomaly_rule_counts(anomaly_items)

    return {
        "clusters": _build_clusters(records),
        "strategies": _build_strategies(records),
        "effort_samples": _build_effort_samples(records),
        "effort_correlation": _round(_pearson(
            [_effort_value(record) for record in records],
            [record["aic_score"] for record in records],
        ), 2),
        "topic_oi_samples": _build_topic_oi_samples(records),
        "similarity_bands": _build_similarity_bands(records),
        "difficulty_adjusted_aic": {
            "overall_mean_aic": _round(overall_mean),
            "summary": summary,
            "students": students,
            "method_note": "Mean-shift adjusted AIC with assignment z-score and percentile rank.",
        },
        "confidence_intervals": confidence_intervals,
        "anomaly_detection": {
            "items": anomaly_items,
            "summary_counts": summary_counts,
            "rule_counts": rule_counts,
            "method_note": "해석 주의 신호이며 조작을 단정하지 않습니다.",
        },
    }


def _record_from_row(row) -> Dict[str, Any]:
    student, assignment, submission, metric = row
    return {
        "student_id": student.id,
        "student_name": student.name,
        "assignment_id": assignment.id,
        "assignment_title": assignment.title,
        "submission_id": submission.id,
        "pi_score": metric.pi_score,
        "ui_score": metric.ui_score,
        "oi_score": metric.oi_score,
        "topic_score": metric.topic_score,
        "aic_score": metric.aic_score,
        "ui_cos_similarity": metric.ui_cos_similarity,
        "ui_distance": metric.ui_distance,
        "ui_newinfo_ratio": metric.ui_newinfo_ratio,
    }


def _mean(values: List[float]) -> float:
    return sum(values) / len(values)


def _sample_std(values: List[float]) -> Optional[float]:
    n = len(values)
    if n < 2:
        return None
    avg = _mean(values)
    variance = sum((value - avg) ** 2 for value in values) / (n - 1)
    return math.sqrt(variance)


def _round(value: Optional[float], digits: int = 1) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), digits)


def _clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return min(max(value, minimum), maximum)


def _difficulty_label(offset: float) -> str:
    if offset >= 5:
        return "hard"
    if offset <= -5:
        return "easy"
    return "normal"


def _difficulty_interpretation(offset: float) -> str:
    if offset >= 5:
        return "상향 보정 참고"
    if offset <= -5:
        return "원점수 보수 해석"
    return "일반 해석"


def _assignment_method_note(n: int) -> str:
    if n < 5:
        return "표본 수가 적어 과제 평균과 상대 위치 해석에 주의가 필요합니다."
    return "과제 평균 차이를 보정하고 과제 내 상대 위치를 함께 표시합니다."


def _percentile_ranks(scores: List[float]) -> Dict[float, float]:
    sorted_scores = sorted(scores)
    ranks_by_score = {}
    for score in sorted(set(sorted_scores)):
        positions = [index + 1 for index, value in enumerate(sorted_scores) if value == score]
        avg_rank = sum(positions) / len(positions)
        ranks_by_score[score] = (avg_rank / len(sorted_scores)) * 100
    return ranks_by_score


def _student_interpretation(percentile_rank: float, offset: float) -> str:
    if percentile_rank >= 75:
        relative = "과제 내 상위권"
    elif percentile_rank >= 50:
        relative = "과제 내 평균 이상"
    elif percentile_rank >= 25:
        relative = "과제 내 중간권"
    else:
        relative = "과제 내 추가 지원 필요 구간"

    if offset >= 5:
        return f"어려운 과제였음을 고려하면 {relative}입니다."
    if offset <= -5:
        return f"쉬운 과제였음을 고려해도 {relative}입니다."
    return f"난이도 보정 후 {relative}입니다."


def _confidence_interval(target_type: str, target_id: Optional[int], target_title: str, scores: List[float]) -> Dict[str, Any]:
    n = len(scores)
    avg = _mean(scores) if scores else None
    std = _sample_std(scores)
    reliability_label = "unstable" if n < 2 else "stable"
    note = "95% t-interval. 향후 표본 누적 시 bootstrap CI로 확장 가능합니다."

    lower = upper = margin = ci_width = None
    if avg is not None and n < 2:
        note = "표본 수가 부족해 신뢰구간을 계산하지 않습니다."
    elif avg is not None and std == 0:
        lower = upper = avg
        margin = 0
        ci_width = 0
    elif avg is not None and std is not None:
        margin = _t_critical_95(n - 1) * std / math.sqrt(n)
        lower = avg - margin
        upper = avg + margin
        ci_width = upper - lower
        if ci_width <= 10:
            reliability_label = "stable"
        elif ci_width <= 20:
            reliability_label = "caution"
            note = "신뢰구간 폭이 넓어 평균 해석에 주의가 필요합니다. 향후 bootstrap CI로 확장 가능합니다."
        else:
            reliability_label = "unstable"
            note = "신뢰구간 폭이 매우 넓어 평균 해석에 주의가 필요합니다. 향후 bootstrap CI로 확장 가능합니다."

    return {
        "target_type": target_type,
        "target_id": target_id,
        "target_title": target_title,
        "metric": "AIC",
        "mean": _round(avg),
        "std": _round(std),
        "n": n,
        "confidence_level": 0.95,
        "lower": _round(lower),
        "upper": _round(upper),
        "ci_width": _round(ci_width),
        "margin": _round(margin),
        "reliability_label": reliability_label,
        "method_note": note,
    }


def _t_critical_95(df: int) -> float:
    table = {
        1: 12.706,
        2: 4.303,
        3: 3.182,
        4: 2.776,
        5: 2.571,
        6: 2.447,
        7: 2.365,
        8: 2.306,
        9: 2.262,
        10: 2.228,
        11: 2.201,
        12: 2.179,
        13: 2.16,
        14: 2.145,
        15: 2.131,
        16: 2.12,
        17: 2.11,
        18: 2.101,
        19: 2.093,
        20: 2.086,
        21: 2.08,
        22: 2.074,
        23: 2.069,
        24: 2.064,
        25: 2.06,
        26: 2.056,
        27: 2.052,
        28: 2.048,
        29: 2.045,
        30: 2.042,
    }
    return table.get(df, 1.96)


def _detect_anomalies(records: List[Dict[str, Any]], z_by_key: Dict[tuple, Optional[float]]) -> List[Dict[str, Any]]:
    items = []
    for record in records:
        z_score = z_by_key.get((record["student_id"], record["assignment_id"]))
        _add_if(items, _draft_dependency_signal(record))
        _add_if(items, _off_topic_originality_signal(record))
        _add_if(items, _low_topic_high_revision_signal(record))
        _add_if(items, _imbalanced_high_score_signal(record, z_score))
        _add_if(items, _overall_low_collaboration_signal(record))
    return items


def _add_if(items: List[Dict[str, Any]], item: Optional[Dict[str, Any]]) -> None:
    if item is not None:
        items.append(item)


def _base_item(record: Dict[str, Any], rule_key: str, label: str, severity: str, evidence: Dict[str, Any], teacher_action: str) -> Dict[str, Any]:
    return {
        "student_id": record["student_id"],
        "student_name": record["student_name"],
        "assignment_id": record["assignment_id"],
        "assignment_title": record["assignment_title"],
        "rule_key": rule_key,
        "label": label,
        "severity": severity,
        "evidence": evidence,
        "teacher_action": teacher_action,
    }


def _draft_dependency_signal(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    similarity = record["ui_cos_similarity"]
    ui = record["ui_score"]
    if similarity is None or ui is None:
        return None
    if similarity >= 0.85 and ui < 50:
        return _base_item(
            record,
            "ai_draft_dependency",
            "AI 초안 의존 가능성",
            "caution",
            f"cos={round(similarity, 2)}, UI={_round(ui)}",
            "초안과 최종본의 변화 과정을 확인하세요.",
        )
    return None


def _off_topic_originality_signal(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    oi = record["oi_score"]
    topic = record["topic_score"]
    if oi is None or topic is None:
        return None
    if oi >= 70 and topic < 50:
        return _base_item(
            record,
            "off_topic_originality",
            "주제 이탈형 독창성",
            "high",
            f"OI={_round(oi)}, TopicScore={_round(topic)}",
            "주제 적합성 피드백 이력을 확인하세요.",
        )
    return None


def _low_topic_high_revision_signal(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ui = record["ui_score"]
    topic = record["topic_score"]
    if ui is None or topic is None:
        return None
    if ui >= 70 and topic < 50:
        return _base_item(
            record,
            "low_topic_high_revision",
            "무의미한 대량 수정 가능성",
            "caution",
            f"UI={_round(ui)}, TopicScore={_round(topic)}",
            "수정량이 과제 주제 적합성 개선으로 이어졌는지 확인하세요.",
        )
    return None


def _imbalanced_high_score_signal(record: Dict[str, Any], z_score: Optional[float]) -> Optional[Dict[str, Any]]:
    scores = [record["pi_score"], record["ui_score"], record["oi_score"]]
    if z_score is None or any(score is None for score in scores):
        return None
    spread = max(scores) - min(scores)
    if z_score >= 2 and spread >= 40:
        return _base_item(
            record,
            "imbalanced_high_score",
            "지표 편중 고득점",
            "high",
            f"z={round(z_score, 2)}, gap={_round(spread)}",
            "높은 AIC가 특정 지표 편중에서 나온 결과인지 확인하세요.",
        )
    return None


def _overall_low_collaboration_signal(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    pi = record["pi_score"]
    ui = record["ui_score"]
    oi = record["oi_score"]
    if pi is None or ui is None or oi is None:
        return None
    if pi < 40 and ui < 40 and oi < 40:
        return _base_item(
            record,
            "overall_low_collaboration",
            "전반적 협업 저하",
            "caution",
            f"PI={_round(pi)}, UI={_round(ui)}, OI={_round(oi)}",
            "질문, 수정, 독창성 전반에 대한 학습 지원을 검토하세요.",
        )
    return None


def _anomaly_summary_counts(items: List[Dict[str, Any]]) -> Dict[str, int]:
    severity_counts = Counter(item["severity"] for item in items)
    return {
        "total": len(items),
        "high": int(severity_counts.get("high", 0)),
        "caution": int(severity_counts.get("caution", 0)),
        "low": int(severity_counts.get("low", 0)),
    }


def _anomaly_rule_counts(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    counts = Counter(item["rule_key"] for item in items)
    rule_order = [
        ("ai_draft_dependency", "AI 초안 의존 가능성", "높은 유사도 + 낮은 UI"),
        ("off_topic_originality", "주제 이탈형 독창성", "높은 OI + 낮은 TopicScore"),
        ("low_topic_high_revision", "무의미한 대량 수정 가능성", "높은 UI + 낮은 TopicScore"),
        ("imbalanced_high_score", "지표 편중 고득점", "높은 z-score + 지표 격차"),
        ("overall_low_collaboration", "전반적 협업 저하", "낮은 PI/UI/OI"),
    ]
    return [
        {
            "rule_key": rule_key,
            "label": label,
            "count": int(counts.get(rule_key, 0)),
            "evidence_summary": evidence_summary,
        }
        for rule_key, label, evidence_summary in rule_order
        if counts.get(rule_key, 0) > 0
    ]


def _build_clusters(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cluster_defs = [
        ("고역량", "#10B981", lambda record: record["aic_score"] >= 80),
        ("중상위", "#3B82F6", lambda record: 65 <= record["aic_score"] < 80),
        ("성장형", "#F97316", lambda record: 50 <= record["aic_score"] < 65),
        ("위험군", "#EF4444", lambda record: record["aic_score"] < 50),
    ]

    clusters = []
    for label, color, predicate in cluster_defs:
        points = [_cluster_point(record) for record in records if predicate(record)]
        clusters.append({
            "label": label,
            "count": len(points),
            "color": color,
            "points": points,
        })
    return clusters


def _cluster_point(record: Dict[str, Any]) -> Dict[str, Any]:
    pi = record["pi_score"] or 0
    ui = record["ui_score"] or 0
    oi = record["oi_score"] or 0
    topic = record["topic_score"] or 0
    aic = record["aic_score"] or 0

    x = ((pi + topic) / 2 - (ui + oi) / 2) / 50
    y = (aic - 50) / 50
    return {
        "x": _round(_clamp(x, -1, 1), 2),
        "y": _round(_clamp(y, -1, 1), 2),
        "student_id": record["student_id"],
        "name": record["student_name"],
        "aic": _round(aic),
    }


def _empty_strategies() -> List[Dict[str, Any]]:
    return [
        {"key": "expert", "title": "Expert", "desc": "질문도 좋고 수정도 많음", "count": 0, "tone": "blue"},
        {"key": "thinker", "title": "Thinker", "desc": "질문은 좋지만 수정 적음", "count": 0, "tone": "yellow"},
        {"key": "editor", "title": "Editor", "desc": "질문은 약하나 수정 많음", "count": 0, "tone": "orange"},
        {"key": "passive", "title": "Passive", "desc": "질문도 약하고 수정도 적음", "count": 0, "tone": "red"},
    ]


def _build_strategies(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    strategies = {item["key"]: item for item in _empty_strategies()}
    for record in records:
        pi = record["pi_score"]
        ui = record["ui_score"]
        if pi is None or ui is None:
            continue
        if pi >= 65 and ui >= 65:
            key = "expert"
        elif pi >= 65:
            key = "thinker"
        elif ui >= 65:
            key = "editor"
        else:
            key = "passive"
        strategies[key]["count"] += 1
    return list(strategies.values())


def _effort_value(record: Dict[str, Any]) -> Optional[float]:
    if record["ui_distance"] is not None:
        return _clamp(record["ui_distance"] * 100)
    if record["ui_cos_similarity"] is not None:
        return _clamp((1 - record["ui_cos_similarity"]) * 100)
    if record["ui_newinfo_ratio"] is not None:
        return _clamp(record["ui_newinfo_ratio"] * 100)
    return record["ui_score"]


def _build_effort_samples(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    samples = []
    for record in records:
        effort = _effort_value(record)
        aic = record["aic_score"]
        if effort is None or aic is None:
            continue
        samples.append({
            "x": _round(effort),
            "y": _round(aic),
            "student_id": record["student_id"],
            "name": record["student_name"],
        })
    return samples


def _build_topic_oi_samples(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    samples = []
    for record in records:
        topic = record["topic_score"]
        oi = record["oi_score"]
        if topic is None or oi is None:
            continue
        samples.append({
            "x": _round(topic),
            "y": _round(oi),
            "student_id": record["student_id"],
            "name": record["student_name"],
        })
    return samples


def _empty_similarity_bands() -> List[Dict[str, Any]]:
    return [
        {"label": "0-40%", "value": 0, "count": 0},
        {"label": "40-60%", "value": 0, "count": 0},
        {"label": "60-80%", "value": 0, "count": 0},
        {"label": "80-100%", "value": 0, "count": 0},
    ]


def _build_similarity_bands(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets = [
        {"label": "0-40%", "scores": []},
        {"label": "40-60%", "scores": []},
        {"label": "60-80%", "scores": []},
        {"label": "80-100%", "scores": []},
    ]
    for record in records:
        similarity = record["ui_cos_similarity"]
        if similarity is None:
            continue
        score = _clamp(similarity * 100)
        if score < 40:
            index = 0
        elif score < 60:
            index = 1
        elif score < 80:
            index = 2
        else:
            index = 3
        buckets[index]["scores"].append(score)

    return [
        {
            "label": bucket["label"],
            "value": _round(_mean(bucket["scores"])) if bucket["scores"] else 0,
            "count": len(bucket["scores"]),
        }
        for bucket in buckets
    ]


def _pearson(xs: List[Optional[float]], ys: List[Optional[float]]) -> Optional[float]:
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 2:
        return None
    paired_xs, paired_ys = zip(*pairs)
    mx, my = sum(paired_xs) / n, sum(paired_ys) / n
    num = sum((x - mx) * (y - my) for x, y in pairs)
    dx = math.sqrt(sum((x - mx) ** 2 for x in paired_xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in paired_ys))
    if dx * dy == 0:
        return None
    return num / (dx * dy)
