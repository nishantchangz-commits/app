"""
app.py — Streamlit front-end for the Hostel Management System.

Run with:
    streamlit run app.py

Default admin login:
    username: admin
    password: admin123
"""

import streamlit as st
import db

st.set_page_config(page_title="Hostel Management System", page_icon="🏠", layout="wide")
db.init_db()

if "user" not in st.session_state:
    st.session_state.user = None


def logout():
    st.session_state.user = None
    st.rerun()


# ------------------------------------------------------------------
# AUTH SCREEN
# ------------------------------------------------------------------
def auth_screen():
    st.title("🏠 Hostel Management System")
    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                user = db.authenticate(username.strip(), password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab_signup:
        with st.form("signup_form"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Choose a Username")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            password = st.text_input("Choose a Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Create Account")
            if submitted:
                if not username or not password or not full_name:
                    st.error("Full name, username, and password are required.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif db.username_exists(username.strip()):
                    st.error("That username is already taken.")
                else:
                    db.create_user(username.strip(), password, full_name.strip(), email, phone)
                    st.success("Account created! Please log in from the Login tab.")


# ------------------------------------------------------------------
# STUDENT VIEW
# ------------------------------------------------------------------
def student_view(user):
    st.title(f"Welcome, {user['full_name']} 👋")
    allocation = db.get_active_allocation(user["id"])

    if allocation:
        st.subheader("🛏️ Your Room Details")
        c1, c2, c3 = st.columns(3)
        c1.metric("Room No.", allocation["room_no"])
        c2.metric("Room Type", allocation["room_type"])
        c3.metric("Fee / Month", f"₹{allocation['fee_per_month']:.0f}")

        st.subheader("📋 Your Important Details")
        details = {
            "Guardian Name": allocation["guardian_name"],
            "Guardian Phone": allocation["guardian_phone"],
            "Emergency Contact": allocation["emergency_contact"],
            "ID Proof Type": allocation["id_proof_type"],
            "ID Proof Number": allocation["id_proof_number"],
            "Blood Group": allocation["blood_group"],
            "Address": allocation["address"],
            "Check-in Date": allocation["check_in_date"],
        }
        left, right = st.columns(2)
        items = list(details.items())
        for i, (label, value) in enumerate(items):
            col = left if i % 2 == 0 else right
            col.write(f"**{label}:** {value or '—'}")

        st.divider()
        if st.button("🚪 Vacate Room"):
            db.vacate_allocation(allocation["id"], allocation["room_id"])
            st.success("Room vacated. Refreshing...")
            st.rerun()

    else:
        st.info("You don't have a room yet. Fill in your details below to get allocated one.")
        rooms = db.get_available_rooms()
        if not rooms:
            st.warning("No rooms are currently available. Please check back later.")
            return

        room_labels = [
            f"{r['room_no']} — {r['room_type']} (Floor {r['floor']}, "
            f"{r['capacity'] - r['occupied']} spot(s) left, ₹{r['fee_per_month']:.0f}/mo)"
            for r in rooms
        ]

        with st.form("allocation_form"):
            st.subheader("🛏️ Choose a Room")
            choice_idx = st.selectbox(
                "Available Rooms", range(len(rooms)), format_func=lambda i: room_labels[i]
            )

            st.subheader("📋 Your Important Details")
            col1, col2 = st.columns(2)
            with col1:
                guardian_name = st.text_input("Guardian Name")
                guardian_phone = st.text_input("Guardian Phone")
                emergency_contact = st.text_input("Emergency Contact")
                blood_group = st.selectbox(
                    "Blood Group",
                    ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
                )
            with col2:
                id_proof_type = st.selectbox(
                    "ID Proof Type", ["Aadhaar", "Passport", "Driving License", "College ID", "Other"]
                )
                id_proof_number = st.text_input("ID Proof Number")
                check_in_date = st.date_input("Check-in Date")
                address = st.text_area("Home Address")

            submitted = st.form_submit_button("Confirm & Allocate Room")
            if submitted:
                if not guardian_name or not guardian_phone or not id_proof_number:
                    st.error("Guardian name, guardian phone, and ID proof number are required.")
                else:
                    room_id = rooms[choice_idx]["id"]
                    details = {
                        "guardian_name": guardian_name,
                        "guardian_phone": guardian_phone,
                        "emergency_contact": emergency_contact,
                        "id_proof_type": id_proof_type,
                        "id_proof_number": id_proof_number,
                        "blood_group": blood_group,
                        "address": address,
                        "check_in_date": str(check_in_date),
                    }
                    try:
                        db.create_allocation(user["id"], room_id, details)
                        st.success("Room allocated successfully!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))


# ------------------------------------------------------------------
# ADMIN VIEW
# ------------------------------------------------------------------
def admin_view(user):
    st.title(f"🛠️ Admin Dashboard — {user['full_name']}")
    tab_rooms, tab_students, tab_add_room = st.tabs(
        ["🏠 Rooms Overview", "👥 Students & Allocations", "➕ Add Room"]
    )

    with tab_rooms:
        rooms = db.get_all_rooms()
        st.dataframe(
            [
                {
                    "Room No.": r["room_no"],
                    "Type": r["room_type"],
                    "Floor": r["floor"],
                    "Capacity": r["capacity"],
                    "Occupied": r["occupied"],
                    "Available": r["capacity"] - r["occupied"],
                    "Fee/Month": r["fee_per_month"],
                }
                for r in rooms
            ],
            use_container_width=True,
            hide_index=True,
        )

    with tab_students:
        allocations = db.get_all_allocations()
        if not allocations:
            st.info("No active allocations yet.")
        for a in allocations:
            with st.expander(f"{a['full_name']} ({a['username']}) — Room {a['room_no']}"):
                c1, c2 = st.columns(2)
                c1.write(f"**Guardian:** {a['guardian_name']} ({a['guardian_phone']})")
                c1.write(f"**Emergency Contact:** {a['emergency_contact']}")
                c1.write(f"**Blood Group:** {a['blood_group']}")
                c2.write(f"**ID Proof:** {a['id_proof_type']} — {a['id_proof_number']}")
                c2.write(f"**Check-in:** {a['check_in_date']}")
                c2.write(f"**Address:** {a['address']}")
                if st.button("Vacate", key=f"vacate_{a['id']}"):
                    db.vacate_allocation(a["id"], a["room_id"])
                    st.rerun()

    with tab_add_room:
        with st.form("add_room_form"):
            room_no = st.text_input("Room No.")
            room_type = st.selectbox("Room Type", ["Single", "Double", "Triple", "Dorm"])
            floor = st.number_input("Floor", min_value=0, step=1)
            capacity = st.number_input("Capacity", min_value=1, step=1)
            fee = st.number_input("Fee per Month (₹)", min_value=0.0, step=100.0)
            submitted = st.form_submit_button("Add Room")
            if submitted:
                try:
                    db.add_room(room_no.strip(), room_type, int(floor), int(capacity), float(fee))
                    st.success(f"Room {room_no} added.")
                except Exception as e:
                    st.error(f"Could not add room: {e}")


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    user = st.session_state.user
    if user is None:
        auth_screen()
        return

    with st.sidebar:
        st.write(f"Logged in as **{user['username']}** ({user['role']})")
        if st.button("Log out"):
            logout()

    if user["role"] == "admin":
        admin_view(user)
    else:
        student_view(user)


if __name__ == "__main__":
    main()
