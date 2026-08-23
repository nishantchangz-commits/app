import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="24-Hour Circular Day Planner", layout="wide")

if "schedule" not in st.session_state:
    st.session_state.schedule = []

def time_to_degrees(time_obj):
    return round((time_obj.hour * 15.0) + (time_obj.minute * 0.25), 2)

st.title("🕒 24-Hour Circular Day Planner")
st.caption("Log activities on a 24-hour circular dial and attach PDFs, Excel sheets, and images.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Add Activity Block")
    title = st.text_input("Activity Title", "Deep Work")
    category = st.selectbox("Category", ["Work", "Fitness", "Rest", "Study", "Personal"])
    color = st.color_picker("Pick Segment Color", "#F59E0B")
    
    t1, t2 = st.columns(2)
    with t1:
        start_time = st.time_input("Start Time", datetime.strptime("09:00", "%H:%M").time())
    with t2:
        end_time = st.time_input("End Time", datetime.strptime("12:00", "%H:%M").time())
        
    uploaded_files = st.file_uploader(
        "Attach Files (PDF, Images, Excel)", 
        type=["pdf", "png", "jpg", "jpeg", "xlsx", "csv"], 
        accept_multiple_files=True
    )
    
    if st.button("Add to Circular Schedule", type="primary"):
        attachments = []
        if uploaded_files:
            for f in uploaded_files:
                attachments.append({
                    "name": f.name,
                    "type": f.type,
                    "size": f.size,
                    "bytes": f.getvalue()
                })
        
        st.session_state.schedule.append({
            "id": len(st.session_state.schedule) + 1,
            "title": title,
            "category": category,
            "color": color,
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
            "start_angle": time_to_degrees(start_time),
            "end_angle": time_to_degrees(end_time),
            "attachments": attachments
        })
        st.success(f"Added '{title}' to schedule!")

with col2:
    st.subheader("24-Hour Circular Visualization")
    if st.session_state.schedule:
        labels = [item["title"] for item in st.session_state.schedule]
        parents = [""] * len(st.session_state.schedule)
        
        values = []
        for item in st.session_state.schedule:
            t_start = datetime.strptime(item["start_time"], "%H:%M")
            t_end = datetime.strptime(item["end_time"], "%H:%M")
            duration = (t_end - t_start).total_seconds() / 60
            values.append(max(duration, 1))
            
        colors = [item["color"] for item in st.session_state.schedule]

        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors),
            hoverinfo="label+value"
        ))
        fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No activities added yet. Use the panel on the left to add your first segment.")

st.divider()
st.subheader("📋 Logged Activities & Attachments")

if st.session_state.schedule:
    for idx, item in enumerate(st.session_state.schedule):
        with st.expander(f"{item['title']} ({item['start_time']} - {item['end_time']}) - [{item['category']}]"):
            st.write(f"**Time Arc:** {item['start_angle']}° to {item['end_angle']}°")
            st.write(f"**Attachments ({len(item['attachments'])}):**")
            
            for file_data in item["attachments"]:
                st.write(f"📎 **{file_data['name']}** ({file_data['type']})")
                
                if "image" in file_data["type"]:
                    st.image(file_data["bytes"], width=250)
                elif "sheet" in file_data["type"] or "csv" in file_data["name"]:
                    try:
                        df = pd.read_csv(file_data["name"]) if "csv" in file_data["name"] else pd.read_excel(file_data["bytes"])
                        st.dataframe(df.head(5))
                    except Exception as e:
                        st.caption("Unable to preview table stream.")
                elif "pdf" in file_data["type"]:
                    st.download_button(
                        label=f"Download {file_data['name']}",
                        data=file_data["bytes"],
                        file_name=file_data["name"],
                        mime="application/pdf"
                    )
