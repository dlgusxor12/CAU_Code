from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import calendar


def tier_id_to_name(tier_id: int) -> str:
    """티어 ID를 티어 이름으로 변환"""
    tier_names = {
        0: "Unrated",
        1: "Bronze V", 2: "Bronze IV", 3: "Bronze III", 4: "Bronze II", 5: "Bronze I",
        6: "Silver V", 7: "Silver IV", 8: "Silver III", 9: "Silver II", 10: "Silver I",
        11: "Gold V", 12: "Gold IV", 13: "Gold III", 14: "Gold II", 15: "Gold I",
        16: "Platinum V", 17: "Platinum IV", 18: "Platinum III", 19: "Platinum II", 20: "Platinum I",
        21: "Diamond V", 22: "Diamond IV", 23: "Diamond III", 24: "Diamond II", 25: "Diamond I",
        26: "Ruby V", 27: "Ruby IV", 28: "Ruby III", 29: "Ruby II", 30: "Ruby I", 31: "Master"
    }
    return tier_names.get(tier_id, "Unknown")


def tier_id_to_color(tier_id: int) -> str:
    """티어 ID를 색상으로 변환"""
    if tier_id == 0:
        return "#000000"  # Black
    elif 1 <= tier_id <= 5:
        return "#CD7F32"  # Bronze
    elif 6 <= tier_id <= 10:
        return "#C0C0C0"  # Silver
    elif 11 <= tier_id <= 15:
        return "#FFD700"  # Gold
    elif 16 <= tier_id <= 20:
        return "#00CED1"  # Platinum
    elif 21 <= tier_id <= 25:
        return "#B9F2FF"  # Diamond
    elif 26 <= tier_id <= 30:
        return "#FF0062"  # Ruby
    else:
        return "#8B00FF"  # Master


def format_solved_ac_user_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """solved.ac API 사용자 데이터를 내부 형식으로 변환"""
    return {
        "handle": raw_data.get("handle", ""),
        "bio": raw_data.get("bio", ""),
        "verified": raw_data.get("verified", False),
        "solved_count": raw_data.get("solvedCount", 0),
        "class_level": raw_data.get("class", 0),
        "tier": raw_data.get("tier", 0),
        "tier_name": tier_id_to_name(raw_data.get("tier", 0)),
        "rating": raw_data.get("rating", 0),
        "rank": raw_data.get("rank", 0),
        "max_streak": raw_data.get("maxStreak", 0),
        "profile_image_url": raw_data.get("profileImageUrl"),
        "joined_at": raw_data.get("joinedAt", ""),
        "coins": raw_data.get("coins", 0),
        "stardusts": raw_data.get("stardusts", 0)
    }


def format_solved_ac_problem_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """solved.ac API 문제 데이터를 내부 형식으로 변환"""
    return {
        "problem_id": raw_data.get("problemId", 0),
        "title": raw_data.get("titleKo", ""),
        "tier": raw_data.get("level", 0),
        "tier_name": tier_id_to_name(raw_data.get("level", 0)),
        "accepted_user_count": raw_data.get("acceptedUserCount", 0),
        "average_tries": raw_data.get("averageTries", 0.0),
        "tags": [tag.get("displayNames", [{}])[0].get("name", "") for tag in raw_data.get("tags", [])],
        "is_solvable": raw_data.get("isSolvable", True),
        "voted_user_count": raw_data.get("votedUserCount", 0)
    }


def generate_contribution_graph_data(year: int = None) -> List[Dict[str, Any]]:
    """기여도 그래프 데이터 생성 (2025년 기준)"""
    if year is None:
        year = 2025

    data = []
    start_date = datetime(year, 1, 1)

    # 365일 또는 366일 (윤년) 데이터 생성
    days_in_year = 366 if calendar.isleap(year) else 365

    for i in range(days_in_year):
        current_date = start_date + timedelta(days=i)
        # 더미 데이터 - 실제로는 solved.ac API에서 가져와야 함
        solved_count = 0  # 기본값, 실제로는 해당 날짜에 푼 문제 수

        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "solved_count": solved_count,
            "day_of_week": current_date.weekday(),
            "week_of_year": current_date.isocalendar()[1]
        })

    return data


def calculate_tier_range_for_recommendations(user_tier: int) -> str:
    """사용자 티어 기반 추천 문제 티어 범위 계산"""
    if user_tier == 0:
        return "b5..b1"
    elif user_tier <= 5:  # Bronze
        return f"b{6-user_tier}..s5"
    elif user_tier <= 10:  # Silver
        return f"b{11-user_tier}..g5"
    elif user_tier <= 15:  # Gold
        return f"s{16-user_tier}..p5"
    elif user_tier <= 20:  # Platinum
        return f"g{21-user_tier}..d5"
    elif user_tier <= 25:  # Diamond
        return f"p{26-user_tier}..r5"
    elif user_tier <= 30:  # Ruby
        return f"d{31-user_tier}..r1"
    else:  # Master
        return "r1..r1"


def estimate_problem_solving_time(tier: int, user_tier: int) -> int:
    """문제 해결 예상 시간 계산 (분 단위)"""
    base_time = 30  # 기본 30분

    difficulty_multiplier = 1.0
    if tier > user_tier:
        difficulty_multiplier = 1.5 + (tier - user_tier) * 0.2
    elif tier < user_tier:
        difficulty_multiplier = max(0.5, 1.0 - (user_tier - tier) * 0.1)

    return int(base_time * difficulty_multiplier)


def format_time_complexity(complexity: str) -> str:
    """시간 복잡도 표준 형식으로 변환"""
    complexity = complexity.strip()
    if not complexity.startswith("O("):
        complexity = f"O({complexity})"
    return complexity


def generate_algorithm_explanation(algorithm_type: str) -> str:
    """알고리즘 유형별 핵심 설명 생성"""
    explanations = {
        "구현": "주어진 조건에 따라 정확히 구현하는 문제로, 코드 작성 능력과 꼼꼼함이 중요합니다.",
        "수학": "수학적 공식이나 정리를 활용하는 문제로, 논리적 사고와 수학적 지식이 필요합니다.",
        "그리디": "매 단계에서 최적의 선택을 하는 알고리즘으로, 증명 가능한 최적해를 구할 수 있습니다.",
        "다이나믹 프로그래밍": "작은 문제의 해를 이용해 큰 문제를 해결하는 방법으로, 최적 부분 구조를 갖습니다.",
        "그래프": "정점과 간선으로 이루어진 구조를 다루며, DFS, BFS, 최단경로 등의 기법을 사용합니다.",
        "문자열": "문자열 처리와 패턴 매칭 문제로, KMP, 라빈-카프 등의 알고리즘을 활용합니다.",
        "브루트포스": "모든 경우의 수를 직접 확인하는 방법으로, 시간 복잡도가 높지만 확실한 해를 보장합니다."
    }

    return explanations.get(algorithm_type, "해당 알고리즘의 핵심 개념을 학습하여 문제 해결 능력을 향상시키세요.")


def calculate_recommendation_accuracy(user_tier: int, recommended_problems: List[Dict]) -> float:
    """추천 정확도 계산"""
    if not recommended_problems:
        return 0.0

    total_score = 0.0
    for problem in recommended_problems:
        problem_tier = problem.get("tier", 0)
        tier_diff = abs(problem_tier - user_tier)

        # 티어 차이에 따른 점수 계산
        if tier_diff <= 1:
            score = 1.0
        elif tier_diff <= 2:
            score = 0.8
        elif tier_diff <= 3:
            score = 0.6
        else:
            score = 0.3

        total_score += score

    return total_score / len(recommended_problems)