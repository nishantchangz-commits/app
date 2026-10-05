"""
Foreign Critics x Indian Food - ratings tracker with photos (single file).

Run:
    pip install streamlit pandas Pillow
    streamlit run indian_food_critics_app.py

Creates `ratings.db` and an `uploads/` folder next to this file.
"""
import datetime as dt
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps

# =====================================================================
# CONFIG
# =====================================================================
st.set_page_config(page_title="Critics on Indian Food", page_icon="🍛", layout="wide")

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "ratings.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

REGIONS = ["North Indian", "South Indian", "East Indian", "West Indian",
           "Street Food", "Mughlai", "Indo-Chinese", "Sweets & Desserts", "Other"]
COUNTRIES = ["USA", "UK", "France", "Italy", "Germany", "Japan", "China", "Australia",
             "Canada", "Spain", "Brazil", "Russia", "UAE", "South Korea", "Other"]
IMG_TYPES = ["jpg", "jpeg", "png", "webp"]


# =====================================================================
# DATABASE
# =====================================================================
@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS critics (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                country     TEXT NOT NULL,
                publication TEXT,
                bio         TEXT,
                photo       TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS reviews (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                critic_id      INTEGER NOT NULL,
                dish           TEXT NOT NULL,
                cuisine_region TEXT,
                restaurant     TEXT,
                city           TEXT,
                rating         REAL NOT NULL CHECK (rating BETWEEN 1 AND 5),
                spice_level    INTEGER CHECK (spice_level BETWEEN 1 AND 5),
                comment        TEXT,
                photo          TEXT,
                visit_date     DATE,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (critic_id) REFERENCES critics(id) ON DELETE CASCADE
            );
            """
        )


# ---------- photos ----------
def save_photo(uploaded_file, prefix="img"):
    """Resize, fix orientation, save as JPEG. Returns stored filename (or None)."""
    if uploaded_file is None:
        return None
    img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((1280, 1280))
    filename = f"{prefix}_{uuid.uuid4().hex[:12]}.jpg"
    img.save(UPLOAD_DIR / filename, "JPEG", quality=85)
    return filename


def photo_path(filename):
    if not filename:
        return None
    p = UPLOAD_DIR / filename
    return str(p) if p.exists() else None


def remove_photo(filename):
    if filename:
        (UPLOAD_DIR / filename).unlink(missing_ok=True)


# ---------- critics ----------
def add_critic(name, country, publication, bio, photo):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO critics (name, country, publication, bio, photo) VALUES (?,?,?,?,?)",
            (name, country, publication, bio, photo),
        )


def get_critics():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM critics ORDER BY name")]


def delete_critic(critic_id):
    with get_conn() as conn:
        photos = [r["photo"] for r in conn.execute(
            "SELECT photo FROM reviews WHERE critic_id = ?", (critic_id,))]
        row = conn.execute("SELECT photo FROM critics WHERE id = ?", (critic_id,)).fetchone()
        if row:
            photos.append(row["photo"])
        conn.execute("DELETE FROM critics WHERE id = ?", (critic_id,))
    for p in photos:
        remove_photo(p)


# ---------- reviews ----------
def add_review(critic_id, dish, region, restaurant, city, rating, spice, comment, photo, visit_date):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO reviews
               (critic_id, dish, cuisine_region, restaurant, city, rating,
                spice_level, comment, photo, visit_date)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (critic_id, dish, region, restaurant, city, rating, spice, comment,
             photo, str(visit_date) if visit_date else None),
        )


def get_reviews_df():
    with get_conn() as conn:
        return pd.read_sql_query(
            """SELECT r.*, c.name AS critic_name, c.country AS critic_country,
                      c.publication, c.photo AS critic_photo
               FROM reviews r JOIN critics c ON c.id = r.critic_id
               ORDER BY r.created_at DESC, r.id DESC""",
            conn,
        )


def delete_review(review_id):
    with get_conn() as conn:
        row = conn.execute("SELECT photo FROM reviews WHERE id = ?", (review_id,)).fetchone()
        conn.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    if row:
        remove_photo(row["photo"])


# =====================================================================
# HELPERS
# =====================================================================
def stars(rating):
    full = int(round(rating))
    return "⭐" * full + "☆" * (5 - full)


def chilies(level):
    return "🌶️" * int(level) if level else "—"


# =====================================================================
# PAGES
# =====================================================================
def page_dashboard():
    st.title("🍛 Foreign Critics on Indian Food")
    df = get_reviews_df()
    critics = get_critics()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Critics", len(critics))
    c2.metric("Reviews", len(df))
    c3.metric("Average rating", f"{df['rating'].mean():.2f} / 5" if len(df) else "—")
    c4.metric("Countries", len({c["country"] for c in critics}))

    if df.empty:
        st.info("No reviews yet. Add a critic, then add their first review from the sidebar.")
        return

    left, right = st.columns(2)
    with left:
        st.subheader("Top dishes")
        st.bar_chart(df.groupby("dish")["rating"].mean().sort_values(ascending=False).head(10))
    with right:
        st.subheader("Rating by critic's country")
        st.bar_chart(df.groupby("critic_country")["rating"].mean().sort_values(ascending=False))

    st.subheader("Rating by cuisine region")
    st.bar_chart(df.groupby("cuisine_region")["rating"].mean())

    st.subheader("Latest reviews")
    cols = st.columns(4)
    for i, (_, row) in enumerate(df.head(8).iterrows()):
        with cols[i % 4]:
            p = photo_path(row["photo"])
            if p:
                st.image(p, use_container_width=True)
            st.markdown(f"**{row['dish']}** {stars(row['rating'])}")
            st.caption(f"{row['critic_name']} ({row['critic_country']})")


def page_browse():
    st.title("🔎 Browse Reviews")
    df = get_reviews_df()
    if df.empty:
        st.info("No reviews yet.")
        return

    f1, f2, f3, f4 = st.columns(4)
    country = f1.multiselect("Critic country", sorted(df["critic_country"].unique()))
    critic = f2.multiselect("Critic", sorted(df["critic_name"].unique()))
    min_rating = f3.slider("Min rating", 1.0, 5.0, 1.0, 0.5)
    search = f4.text_input("Search dish / restaurant / city")

    if country:
        df = df[df["critic_country"].isin(country)]
    if critic:
        df = df[df["critic_name"].isin(critic)]
    df = df[df["rating"] >= min_rating]
    if search:
        s = search.lower()
        df = df[df["dish"].str.lower().str.contains(s, na=False)
                | df["restaurant"].fillna("").str.lower().str.contains(s)
                | df["city"].fillna("").str.lower().str.contains(s)]

    st.caption(f"{len(df)} review(s)")
    for _, r in df.iterrows():
        with st.container(border=True):
            img_col, text_col = st.columns([1, 2])
            with img_col:
                p = photo_path(r["photo"])
                if p:
                    st.image(p, use_container_width=True)
                else:
                    st.caption("No dish photo")
            with text_col:
                st.subheader(r["dish"])
                st.markdown(f"{stars(r['rating'])} **{r['rating']}/5** · Spice {chilies(r['spice_level'])}")
                where = " · ".join(x for x in [r["restaurant"], r["city"], r["cuisine_region"]] if x)
                if where:
                    st.write(f"📍 {where}")
                if r["comment"]:
                    st.markdown(f"> {r['comment']}")
                a, b = st.columns([1, 6])
                cp = photo_path(r["critic_photo"])
                if cp:
                    a.image(cp, width=48)
                pub = f", {r['publication']}" if r["publication"] else ""
                b.caption(f"{r['critic_name']} ({r['critic_country']}){pub} · visited {r['visit_date'] or 'n/a'}")


def page_add_review():
    st.title("📝 Add a Review")
    critics = get_critics()
    if not critics:
        st.warning("Please add a critic first.")
        return

    labels = {f"{c['name']} ({c['country']})": c["id"] for c in critics}
    with st.form("review_form", clear_on_submit=True):
        critic_label = st.selectbox("Critic *", list(labels))
        col1, col2 = st.columns(2)
        dish = col1.text_input("Dish *", placeholder="e.g. Butter Chicken")
        region = col2.selectbox("Cuisine region", REGIONS)
        col3, col4 = st.columns(2)
        restaurant = col3.text_input("Restaurant / Stall")
        city = col4.text_input("City")
        col5, col6, col7 = st.columns(3)
        rating = col5.slider("Rating", 1.0, 5.0, 4.0, 0.5)
        spice = col6.slider("Spice level 🌶️", 1, 5, 3)
        visit_date = col7.date_input("Date of visit", dt.date.today())
        comment = st.text_area("Critic's comment")
        photo = st.file_uploader("Dish photo", type=IMG_TYPES)
        submitted = st.form_submit_button("Save review", type="primary")

    if submitted:
        if not dish.strip():
            st.error("Dish name is required.")
            return
        try:
            fname = save_photo(photo, "dish")
        except Exception as e:
            st.error(f"Could not read the image: {e}")
            return
        add_review(labels[critic_label], dish.strip(), region, restaurant.strip(),
                   city.strip(), rating, spice, comment.strip(), fname, visit_date)
        st.success("Review saved! 🎉")


def page_add_critic():
    st.title("➕ Add a Critic")
    with st.form("critic_form", clear_on_submit=True):
        name = st.text_input("Name *")
        col1, col2 = st.columns(2)
        country = col1.selectbox("Country *", COUNTRIES)
        publication = col2.text_input("Publication / Channel")
        bio = st.text_area("Short bio")
        photo = st.file_uploader("Critic photo", type=IMG_TYPES)
        submitted = st.form_submit_button("Save critic", type="primary")

    if submitted:
        if not name.strip():
            st.error("Name is required.")
            return
        try:
            fname = save_photo(photo, "critic")
        except Exception as e:
            st.error(f"Could not read the image: {e}")
            return
        add_critic(name.strip(), country, publication.strip(), bio.strip(), fname)
        st.success(f"Added {name}!")


def page_manage():
    st.title("🗂️ Manage Data")
    tab1, tab2 = st.tabs(["Reviews", "Critics"])

    with tab1:
        df = get_reviews_df()
        if df.empty:
            st.info("No reviews.")
        for _, r in df.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.write(f"**{r['dish']}**, {r['rating']}/5 by {r['critic_name']}")
            if c2.button("Delete", key=f"dr{r['id']}"):
                delete_review(int(r["id"]))
                st.rerun()

    with tab2:
        critics = get_critics()
        if not critics:
            st.info("No critics.")
        for c in critics:
            c1, c2 = st.columns([5, 1])
            c1.write(f"**{c['name']}** ({c['country']})")
            if c2.button("Delete", key=f"dc{c['id']}", help="Also deletes all their reviews"):
                delete_critic(c["id"])
                st.rerun()


# =====================================================================
# MAIN / ROUTER
# =====================================================================
def main():
    init_db()
    pages = {
        "🏠 Dashboard": page_dashboard,
        "🔎 Browse Reviews": page_browse,
        "📝 Add Review": page_add_review,
        "➕ Add Critic": page_add_critic,
        "🗂️ Manage": page_manage,
    }
    choice = st.sidebar.radio("Navigate", list(pages))
    pages[choice]()


main()
