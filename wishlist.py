"""
Wishlist module - Flask blueprint for anime wishlist management.
Provides routes to list, filter, and manage anime wishlist entries.
"""

from flask import Blueprint, jsonify, render_template, request

wishlist_bp = Blueprint("wishlist", __name__, url_prefix="/wishlist")

# French → English genre translation map
GENRE_TRANSLATIONS = {
    "Action": "Action",
    "Aventure": "Adventure",
    "Comédie": "Comedy",
    "Comédie Romantique": "Romantic Comedy",
    "Drame": "Drama",
    "Fantastique": "Fantasy",
    "Horreur": "Horror",
    "Mystère": "Mystery",
    "Romance": "Romance",
    "Science-Fiction": "Science Fiction",
    "Sci-Fi": "Science Fiction",
    "Tranche de vie": "Slice of Life",
    "Vie quotidienne": "Slice of Life",
    "Surnaturel": "Supernatural",
    "Thriller": "Thriller",
    "Psychologique": "Psychological",
    "Musique": "Music",
    "Sport": "Sports",
    "Magie": "Magic",
    "Arts martiaux": "Martial Arts",
    "Combat": "Martial Arts",
    "Mecha": "Mecha",
    "Jeux": "Games",
    "Ecchi": "Ecchi",
    "Harem": "Harem",
    "Isekai": "Isekai",
    "Vampires": "Vampire",
    "Démons": "Demons",
    "Super Pouvoirs": "Super Power",
    "Pouvoirs surnaturels": "Super Power",
    "Militaire": "Military",
    "Police": "Police",
    "Espace": "Space",
    "Voyage dans le temps": "Time Travel",
    "Enquête": "Mystery",
    "Shōnen": "Shounen",
    "Shōjo": "Shoujo",
    "Seinen": "Seinen",
    "Josei": "Josei",
    "Yaoi": "Yaoi",
    "Yuri": "Yuri",
}


def translate_genre(genre: str) -> str:
    """
    Translate a genre string from French to English if a mapping exists.
    Used when ingesting data from external sources (e.g. Supabase) that may
    still contain French genre names.
    """
    return GENRE_TRANSLATIONS.get(genre, genre)


def get_wishlist_data():
    """
    Return all wishlist entries. In production this calls Supabase;
    here we use representative mock data so the UI can be previewed locally.
    """
    return [
        {
            "id": 1,
            "title": "Fullmetal Alchemist: Brotherhood",
            "status": "Wishlist",
            "score": None,
            "episodes": 64,
            "genres": ["Action", "Adventure", "Drama", "Fantasy"],
            "tags": ["Alchemy", "Shounen", "Military", "Brothers"],
        },
        {
            "id": 2,
            "title": "Steins;Gate",
            "status": "Wishlist",
            "score": None,
            "episodes": 24,
            "genres": ["Science Fiction", "Thriller", "Drama"],
            "tags": ["Time Travel", "Psychological", "Visual Novel"],
        },
        {
            "id": 3,
            "title": "Attack on Titan",
            "status": "Watching",
            "score": 9,
            "episodes": 87,
            "genres": ["Action", "Drama", "Fantasy", "Mystery"],
            "tags": ["Military", "Shounen", "Post-Apocalyptic", "Gore"],
        },
        {
            "id": 4,
            "title": "Your Lie in April",
            "status": "Completed",
            "score": 10,
            "episodes": 22,
            "genres": ["Drama", "Music", "Romance"],
            "tags": ["Music", "School", "Coming of Age"],
        },
        {
            "id": 5,
            "title": "Hunter x Hunter (2011)",
            "status": "Wishlist",
            "score": None,
            "episodes": 148,
            "genres": ["Action", "Adventure", "Fantasy"],
            "tags": ["Shounen", "Supernatural", "Tournament"],
        },
        {
            "id": 6,
            "title": "Neon Genesis Evangelion",
            "status": "Wishlist",
            "score": None,
            "episodes": 26,
            "genres": ["Action", "Drama", "Mecha", "Psychological", "Science Fiction"],
            "tags": ["Mecha", "Psychological", "Post-Apocalyptic"],
        },
        {
            "id": 7,
            "title": "Violet Evergarden",
            "status": "Completed",
            "score": 9,
            "episodes": 13,
            "genres": ["Adventure", "Drama", "Fantasy"],
            "tags": ["Military", "Healing", "Letters"],
        },
        {
            "id": 8,
            "title": "Re:Zero",
            "status": "Watching",
            "score": 8,
            "episodes": 50,
            "genres": ["Action", "Drama", "Fantasy", "Psychological"],
            "tags": ["Isekai", "Time Travel", "Supernatural", "Psychological"],
        },
        {
            "id": 9,
            "title": "Spy x Family",
            "status": "Wishlist",
            "score": None,
            "episodes": 25,
            "genres": ["Action", "Comedy"],
            "tags": ["Shounen", "Family", "Spy"],
        },
        {
            "id": 10,
            "title": "Death Note",
            "status": "Completed",
            "score": 9,
            "episodes": 37,
            "genres": ["Mystery", "Psychological", "Supernatural", "Thriller"],
            "tags": ["Psychological", "Police", "Supernatural"],
        },
        {
            "id": 11,
            "title": "Demon Slayer",
            "status": "Watching",
            "score": 8,
            "episodes": 44,
            "genres": ["Action", "Adventure", "Fantasy"],
            "tags": ["Shounen", "Demons", "Swords"],
        },
        {
            "id": 12,
            "title": "Sword Art Online",
            "status": "Completed",
            "score": 7,
            "episodes": 25,
            "genres": ["Action", "Adventure", "Fantasy", "Romance", "Science Fiction"],
            "tags": ["Isekai", "Games", "Virtual Reality"],
        },
        {
            "id": 13,
            "title": "One Punch Man",
            "status": "Wishlist",
            "score": None,
            "episodes": 24,
            "genres": ["Action", "Comedy"],
            "tags": ["Superhero", "Parody", "Seinen"],
        },
        {
            "id": 14,
            "title": "Fruits Basket",
            "status": "Wishlist",
            "score": None,
            "episodes": 63,
            "genres": ["Comedy", "Drama", "Romance", "Slice of Life"],
            "tags": ["Shoujo", "School", "Supernatural"],
        },
        {
            "id": 15,
            "title": "Cowboy Bebop",
            "status": "Wishlist",
            "score": None,
            "episodes": 26,
            "genres": ["Action", "Adventure", "Drama", "Science Fiction"],
            "tags": ["Space", "Bounty Hunter", "Jazz"],
        },
    ]


def _count_occurrences(entries: list, field: str) -> list[dict]:
    """
    Count how many times each value appears across all entries for a given list field.
    Returns [{"name": ..., "count": ...}, ...] sorted by count descending.
    """
    counts: dict[str, int] = {}
    for entry in entries:
        for value in entry.get(field, []):
            counts[value] = counts.get(value, 0) + 1
    return sorted(
        [{"name": name, "count": count} for name, count in counts.items()],
        key=lambda x: (-x["count"], x["name"]),
    )


@wishlist_bp.route("/")
def index():
    """Render the wishlist page."""
    return render_template("wishlist.html")


@wishlist_bp.route("/api/entries")
def api_entries():
    """
    Return wishlist entries, optionally filtered by genres and/or tags.

    Query parameters:
      genres  – comma-separated list of genres to filter by (AND logic)
      tags    – comma-separated list of tags to filter by (AND logic)
      status  – filter by status string (exact match)
      search  – case-insensitive title substring search
    """
    entries = get_wishlist_data()

    genre_filter = [g.strip() for g in request.args.get("genres", "").split(",") if g.strip()]
    tag_filter = [t.strip() for t in request.args.get("tags", "").split(",") if t.strip()]
    status_filter = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip().lower()

    if genre_filter:
        entries = [e for e in entries if all(g in e["genres"] for g in genre_filter)]
    if tag_filter:
        entries = [e for e in entries if all(t in e["tags"] for t in tag_filter)]
    if status_filter:
        entries = [e for e in entries if e["status"].lower() == status_filter.lower()]
    if search:
        entries = [e for e in entries if search in e["title"].lower()]

    return jsonify(entries)


@wishlist_bp.route("/api/genres")
def api_genres():
    """
    Return all genres with their occurrence counts across all wishlist entries.
    Results are sorted by count descending then alphabetically.
    All genre names are in English.
    """
    entries = get_wishlist_data()
    return jsonify(_count_occurrences(entries, "genres"))


@wishlist_bp.route("/api/tags")
def api_tags():
    """
    Return all tags with their occurrence counts across all wishlist entries.
    Results are sorted by count descending then alphabetically.
    """
    entries = get_wishlist_data()
    return jsonify(_count_occurrences(entries, "tags"))


# ---------------------------------------------------------------------------
# Standalone app entry-point (development only)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    from flask import Flask

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.register_blueprint(wishlist_bp)

    @app.route("/")
    def root():
        from flask import redirect

        return redirect("/wishlist/")

    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, port=5001)
