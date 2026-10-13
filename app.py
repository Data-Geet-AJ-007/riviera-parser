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
        lines = [line.strip() for line in raw_text.split('\n')]
        
        records = []
        i = 0
        sr_no = 1

        while i < len(lines):
            line = lines[i]
            
            # Look for a line that looks like a room number (short standalone number, e.g. "17", "9", or typical room numbers)
            # Or lines that contain guest names followed by IDs and dates.
            # Let's target the layout where a name appears, followed by a long ID number, then dates.
            
            # Check if current line is a potential guest name (not a date, number, block name, or status)
            if line and not re.match(r'^\d{2}/\d{2}/\d{4}$', line) and not line.isdigit() and '-' not in line and '#' not in line:
                if line not in ["New Guest", "Dirty", "Group", "No Allotment Block"]:
                    name = line
                    room_num = "N/A"
                    room_type = "N/A"
                    pax = "N/A"
                    
                    # Scan ahead for room info or block headers nearby
                    # Look backwards or forwards for a short room number or block indicator
                    for j in range(max(0, i - 3), i):
                        if lines[j].isdigit() and len(lines[j]) <= 3:
                            room_num = lines[j]
                    
                    # Look downwards for the numbers at the tail end of the guest block (pax count)
                    # Riviera data format typically ends blocks with numbers like: 1 \n 1 \n 0 or similar
                    for k in range(i + 1, min(len(lines), i + 10)):
                        # If we hit a date or ID, keep going
                        if re.match(r'^\d{13,}$', lines[k]): # Long ID number
                            pass
                        elif re.match(r'^\d{2}/\d{2}/\d{4}$', lines[k]): # Date
                            pass
                        elif lines[k].isdigit() and len(lines[k]) == 1:
                            # Usually the last few single digits are adults/children/infants counts
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

        # Fallback line-by-line cleaner approach if the above structured scan misses entries
        if not records:
            # Universal pattern: Extract lines that look like guest names
            pass

        if not records:
            st.error("No valid guest data found. Please check your format.")
        else:
            df = pd.DataFrame(records)
            st.success("Data processed successfully!")
            st.dataframe(df, use_container_width=True)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Riviera Dashboard - Guest Summary", ln=True, align='C')
            pdf.ln(10)
            
            col_widths = [15, 60, 25, 45, 25]
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
                
            pdf_bytes = bytes(pdf.output())

            st.download_button(
                label="Yes (Download PDF)",
                data=pdf_bytes,
                file_name="guest_summary.pdf",
                mime="application/pdf",
                type="secondary"
            )
