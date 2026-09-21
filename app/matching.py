from app.extensions import db
from app.models.post import Post
from app.models.match import Match

COMPLEMENTARY_TYPES = {
    "objet_perdu": "objet_retrouve",
    "objet_retrouve": "objet_perdu",
    "personne_disparue": "personne_retrouvee",
    "personne_retrouvee": "personne_disparue",
}

WEIGHTS = {
    "category": 15,
    "brand": 20,
    "color": 10,
    "location": 15,
    "date": 10,
    "title_similarity": 30,
}


def word_overlap_score(text1, text2):
    if not text1 or not text2:
        return 0
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0
    common = words1 & words2
    return len(common) / max(len(words1), len(words2))


def date_proximity_score(date1, date2, max_days=30):
    if not date1 or not date2:
        return 0
    diff_days = abs((date1 - date2).days)
    if diff_days > max_days:
        return 0
    return 1 - (diff_days / max_days)


def compute_score(post_a, post_b):
    score = 0

    if post_a.category_id and post_b.category_id and post_a.category_id == post_b.category_id:
        score += WEIGHTS["category"]

    if post_a.brand and post_b.brand and post_a.brand.strip().lower() == post_b.brand.strip().lower():
        score += WEIGHTS["brand"]

    if post_a.color and post_b.color and post_a.color.strip().lower() == post_b.color.strip().lower():
        score += WEIGHTS["color"]

    if post_a.location and post_b.location and post_a.location.strip().lower() == post_b.location.strip().lower():
        score += WEIGHTS["location"]

    score += WEIGHTS["date"] * date_proximity_score(post_a.date_event, post_b.date_event)

    text_a = f"{post_a.title} {post_a.description or ''}"
    text_b = f"{post_b.title} {post_b.description or ''}"
    score += WEIGHTS["title_similarity"] * word_overlap_score(text_a, text_b)

    return round(score, 1)


def score_to_level(score):
    if score >= 75:
        return "elevee"
    elif score >= 45:
        return "moyenne"
    return None


def find_matches_for_post(post):
    """Cherche des correspondances pour un signalement donné parmi les posts actifs complémentaires."""
    complementary_type = COMPLEMENTARY_TYPES.get(post.type)
    if not complementary_type:
        return []

    candidates_query = Post.query.filter(
        Post.type == complementary_type,
        Post.status == "active",
        Post.id != post.id,
    )

    # Même pays, sauf si l'un des deux est en diffusion internationale
    if not post.is_international:
        candidates_query = candidates_query.filter(
            (Post.country_id == post.country_id) | (Post.is_international == True)
        )

    candidates = candidates_query.all()
    new_matches = []

    for candidate in candidates:
        already_exists = Match.query.filter(
            ((Match.post_id_1 == post.id) & (Match.post_id_2 == candidate.id)) |
            ((Match.post_id_1 == candidate.id) & (Match.post_id_2 == post.id))
        ).first()

        if already_exists:
            continue

        score = compute_score(post, candidate)
        level = score_to_level(score)

        if level:
            match = Match(
                post_id_1=post.id,
                post_id_2=candidate.id,
                score=score,
                level=level,
                status="proposee",
            )
            db.session.add(match)
            new_matches.append(match)

    db.session.commit()
    return new_matches