import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="India Deity Darshan",
    page_icon="🛕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Data
# -----------------------------
DEITIES = [
    {
        "name": "Lord Shiva",
        "category": "Shiva",
        "state": "Uttarakhand",
        "temple": "Kedarnath Temple",
        "location": "Kedarnath, Uttarakhand",
        "description": "One of the most revered Shiva temples in India and one of the twelve Jyotirlingas.",
        "image": "shiva.jpg",
    },
    {
        "name": "Lord Vishnu",
        "category": "Vishnu",
        "state": "Uttarakhand",
        "temple": "Badrinath Temple",
        "location": "Badrinath, Uttarakhand",
        "description": "A major pilgrimage shrine dedicated to Lord Vishnu in the form of Badrinarayan.",
        "image": "vishnu.jpg",
    },
    {
        "name": "Lord Venkateswara",
        "category": "Vishnu",
        "state": "Andhra Pradesh",
        "temple": "Tirumala Venkateswara Temple",
        "location": "Tirumala, Andhra Pradesh",
        "description": "A famous Vaishnavite pilgrimage center dedicated to Lord Venkateswara.",
        "image": "venkateswara.jpg",
    },
    {
        "name": "Lord Krishna",
        "category": "Krishna",
        "state": "Uttar Pradesh",
        "temple": "Banke Bihari Temple",
        "location": "Vrindavan, Uttar Pradesh",
        "description": "A celebrated Krishna temple in the sacred town of Vrindavan.",
        "image": "krishna.jpg",
    },
    {
        "name": "Lord Rama",
        "category": "Rama",
        "state": "Uttar Pradesh",
        "temple": "Shri Ram Janmabhoomi",
        "location": "Ayodhya, Uttar Pradesh",
        "description": "A major pilgrimage destination associated with Lord Rama and Ayodhya.",
        "image": "rama.jpg",
    },
    {
        "name": "Lord Jagannath",
        "category": "Jagannath",
        "state": "Odisha",
        "temple": "Jagannath Temple",
        "location": "Puri, Odisha",
        "description": "One of India's major pilgrimage temples, dedicated to Lord Jagannath.",
        "image": "jagannath.jpg",
    },
    {
        "name": "Lord Ganesha",
        "category": "Ganesha",
        "state": "Maharashtra",
        "temple": "Siddhivinayak Temple",
        "location": "Mumbai, Maharashtra",
        "description": "A well-known Ganesha temple visited by devotees throughout the year.",
        "image": "ganesha.jpg",
    },
    {
        "name": "Goddess Durga",
        "category": "Durga",
        "state": "Jammu and Kashmir",
        "temple": "Vaishno Devi Shrine",
        "location": "Katra, Jammu and Kashmir",
        "description": "A major Shakti pilgrimage site in the Trikuta Mountains.",
        "image": "durga.jpg",
    },
    {
        "name": "Goddess Lakshmi",
        "category": "Lakshmi",
        "state": "Tamil Nadu",
        "temple": "Kamakshi Amman Temple",
        "location": "Kanchipuram, Tamil Nadu",
        "description": "A historic South Indian temple dedicated to Goddess Kamakshi.",
        "image": "lakshmi.jpg",
    },
    {
        "name": "Goddess Meenakshi",
        "category": "Shakti",
        "state": "Tamil Nadu",
        "temple": "Meenakshi Amman Temple",
        "location": "Madurai, Tamil Nadu",
        "description": "A spectacular historic temple complex dedicated to Goddess Meenakshi and Lord Sundareswarar.",
        "image": "meenakshi.jpg",
    },
    {
        "name": "Mahakaleshwar",
        "category": "Shiva",
        "state": "Madhya Pradesh",
        "temple": "Mahakaleshwar Jyotirlinga",
        "location": "Ujjain, Madhya Pradesh",
        "description": "One of the twelve Jyotirlingas and an important Shaiva pilgrimage center.",
        "image": "mahakaleshwar.jpg",
    },
    {
        "name": "Somnath",
        "category": "Shiva",
        "state": "Gujarat",
        "temple": "Somnath Temple",
        "location": "Prabhas Patan, Gujarat",
        "description": "One of the twelve Jyotirlingas, located on the Arabian Sea coast.",
        "image": "somnath.jpg",
    },
]

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #fff8ed 0%, #fffdf8 55%, #f8efe3 100%);
    }

    .hero {
        padding: 34px 30px;
        border-radius: 24px;
        background: linear-gradient(135deg, #7b1e0e, #b84a16);
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 10px 30px rgba(90, 40, 10, .18);
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 18px;
        opacity: .95;
    }

    .card {
        background: rgba(255,255,255,.94);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 18px;
        border: 1px solid #ead9c5;
        box-shadow: 0 6px 18px rgba(80,50,20,.08);
        min-height: 250px;
    }

    .card h3 {
        color: #7b1e0e;
        margin: 8px 0 4px 0;
    }

    .tag {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        background: #fff0dc;
        color: #8a3b12;
        font-size: 12px;
        margin-right: 5px;
    }

    .quote {
        text-align: center;
        font-size: 20px;
        color: #7b1e0e;
        font-weight: 600;
        padding: 25px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #ead9c5;
        padding: 15px;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
IMAGE_DIR = Path(__file__).parent / "images"

def show_image(filename):
    path = IMAGE_DIR / filename
    if path.exists():
        st.image(str(path), use_container_width=True)
    else:
        st.markdown(
            "<div style='height:170px;display:flex;align-items:center;"
            "justify-content:center;background:#fff3e3;border-radius:14px;"
            "font-size:55px;'>🛕</div>",
            unsafe_allow_html=True,
        )

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>🛕 India Deity Darshan</h1>
    <p>Explore the sacred temples and revered deities of India — all in one place.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🕉️ Darshan Menu")
page = st.sidebar.radio(
    "Choose a section",
    ["🏠 Home", "🙏 Deities", "🛕 Temples", "📍 Temple Finder", "ℹ️ About"]
)

# -----------------------------
# Home
# -----------------------------
if page == "🏠 Home":
    st.subheader("Welcome to India Deity Darshan")

    c1, c2, c3 = st.columns(3)
    c1.metric("🙏 Deity Profiles", len(DEITIES))
    c2.metric("🛕 Featured Temples", len(DEITIES))
    c3.metric("🇮🇳 States/UTs", len(set(d["state"] for d in DEITIES)))

    st.markdown('<div class="quote">"May your journey through India's sacred places bring peace, devotion and inspiration."</div>', unsafe_allow_html=True)

    st.subheader("✨ Featured Darshan")
    cols = st.columns(3)
    for i, deity in enumerate(DEITIES[:6]):
        with cols[i % 3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            show_image(deity["image"])
            st.markdown(f"### {deity['name']}")
            st.markdown(f"**🛕 {deity['temple']}**")
            st.caption(deity["location"])
            st.write(deity["description"])
            st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Deities
# -----------------------------
elif page == "🙏 Deities":
    st.subheader("🙏 Explore Deities")

    search = st.text_input("🔎 Search deity, temple or state")
    categories = ["All"] + sorted(set(d["category"] for d in DEITIES))
    category = st.selectbox("Deity category", categories)

    filtered = DEITIES

    if category != "All":
        filtered = [d for d in filtered if d["category"] == category]

    if search:
        q = search.lower()
        filtered = [
            d for d in filtered
            if q in d["name"].lower()
            or q in d["temple"].lower()
            or q in d["state"].lower()
            or q in d["location"].lower()
        ]

    st.write(f"Showing **{len(filtered)}** result(s).")

    cols = st.columns(3)
    for i, deity in enumerate(filtered):
        with cols[i % 3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            show_image(deity["image"])
            st.markdown(f"### {deity['name']}")
            st.markdown(
                f"<span class='tag'>{deity['category']}</span>"
                f"<span class='tag'>{deity['state']}</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"**🛕 {deity['temple']}**")
            st.caption(deity["location"])
            st.write(deity["description"])
            st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Temples
# -----------------------------
elif page == "🛕 Temples":
    st.subheader("🛕 Sacred Temples of India")

    states = ["All"] + sorted(set(d["state"] for d in DEITIES))
    selected_state = st.selectbox("Select state / UT", states)

    data = DEITIES if selected_state == "All" else [
        d for d in DEITIES if d["state"] == selected_state
    ]

    for deity in data:
        with st.expander(f"🛕 {deity['temple']} — {deity['location']}"):
            left, right = st.columns([1, 2])
            with left:
                show_image(deity["image"])
            with right:
                st.markdown(f"## {deity['name']}")
                st.write(deity["description"])
                st.write(f"**State:** {deity['state']}")
                st.write(f"**Location:** {deity['location']}")
                st.info("You can add temple timings, history, festivals, travel information and official links to this record later.")

# -----------------------------
# Temple Finder
# -----------------------------
elif page == "📍 Temple Finder":
    st.subheader("📍 Temple Finder")

    st.write("Select a state to discover featured temples in that region.")

    state = st.selectbox(
        "State / UT",
        sorted(set(d["state"] for d in DEITIES))
    )

    matches = [d for d in DEITIES if d["state"] == state]

    for d in matches:
        st.markdown(f"### 🛕 {d['temple']}")
        st.write(f"**Deity:** {d['name']}")
        st.write(f"**Location:** {d['location']}")

        # Google Maps search link without requiring an API key
        maps_query = d["location"].replace(" ", "+")
        st.markdown(
            f"[🗺️ Open location in Google Maps](https://www.google.com/maps/search/?api=1&query={maps_query})"
        )
        st.divider()

# -----------------------------
# About
# -----------------------------
else:
    st.subheader("ℹ️ About the App")

    st.write("""
    **India Deity Darshan** is a Streamlit application for exploring India's
    diverse devotional traditions, temples and pilgrimage destinations.

    The application is intentionally designed so you can add your own:
    - deity photographs
    - temple photographs
    - temple history
    - timings
    - festivals
    - mantras
    - locations
    - official temple websites
    - additional states and temples
    """)

    st.warning(
        "Temple timings and travel information should be verified from official "
        "temple or tourism sources before visiting."
    )

st.markdown("---")
st.caption("🕉️ India Deity Darshan • A devotional exploration project")
