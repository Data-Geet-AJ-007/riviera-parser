import re
import pandas as pd
from fpdf import FPDF
import streamlit as st

st.set_page_config(page_title="Riviera Dashboard Parser", layout="centered")

st.title("🏨 Riviera Dashboard Guest Parser")
st.markdown("Paste your dashboard data below:")

raw_text = st.text_area("Dashboard Data Input", height=250, placeholder="Paste data here...")

if st.button("Process Data", type="primary"):
    if not raw_text.strip():
        st.warning("Please paste some data first.")
    else:
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        records = []
        i = 0
        sr_no = 1

        while i < len(lines):
            room_match = re.match(r'^(\d+)\s*-\s*(.+)$', lines[i])
            if room_match:
                room_num = room_match.group(1)
                room_type = room_match.group(2)

                name = "N/A"
                for j in range(max(0, i - 4), i):
                    line = lines[j]
                    if not re.search(r'^\d+$', line) and '/' not in line and line not in ["New Guest", "No Allotment Block"]:
                        name = line

                pax = "N/A"
                for k in range(i + 1, min(len(lines), i + 6)):
                    if lines[k].isdigit() and int(lines[k]) < 10:
                        pax = lines[k]

                records.append({
                    "Sr. No.": sr_no,
                    "Name of the Guest": name,
                    "Room Number": room_num,
                    "Type of Room": room_type,
                    "Number of Pax": pax
                })
                sr_no += 1
            i += 1

        if not records:
            st.error("No valid room data found. Please check your format.")
        else:
            df = pd.DataFrame(records)
            st.success("Data processed successfully!")
            st.dataframe(df, use_container_width=True)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Riviera Dashboard - Guest Summary", ln=True, align='C')
            pdf.ln(10)

            col_widths = [15, 50, 25, 65, 25]
            headers = ["Sr.", "Name", "Room", "Room Type", "Pax"]

            pdf.set_font("Arial", 'B', 10)
            for idx, h in enumerate(headers):
                pdf.cell(col_widths[idx], 10, h, border=1, align='C')
            pdf.ln()

            pdf.set_font("Arial", size=9)
            for _, row in df.iterrows():
                pdf.cell(col_widths[0], 10, str(row["Sr. No."]), border=1, align='C')
                pdf.cell(col_widths[1], 10, str(row["Name of the Guest"]), border=1)
                pdf.cell(col_widths[2], 10, str(row["Room Number"]), border=1, align='C')
                pdf.cell(col_widths[3], 10, str(row["Type of Room"]), border=1)
                pdf.cell(col_widths[4], 10, str(row["Number of Pax"]), border=1, align='C')
                pdf.ln()

            pdf_bytes = pdf.output(dest='S').encode('latin1')

            st.download_button(
                label="Yes (Download PDF)",
                data=pdf_bytes,
                file_name="guest_summary.pdf",
                mime="application/pdf",
                type="secondary"
            )
