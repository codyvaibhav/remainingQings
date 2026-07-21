import streamlit as st
from datetime import datetime
import pandas as pd
from config import main

def show():
    st.set_page_config(page_title=f"{main} Improvement", page_icon=":memo:")
    st.title("Improvements")
    st.markdown(
        """
        <style>
        .stButton>button {
            margin-top: 20px !important;
            background-color: #4EAD44 !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 8px 16px !important;
            border: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize session_state for df_improvement if not exists
    if 'df_improvement' not in st.session_state:
        # Initial data with Imp. Applied Date column
        data = [
            {
                'Symptom': 'Display',
                'Case Code': 'P260302-06393/P260303-09985/P260309-00277/P260312-09076',
                'Progr.Stat.': 'Resolve - Released',
                'Sub-Symptom': 'Flickering 8K',
                'Imp. Applied Date': datetime(2026, 3, 10).date(),
                'Improvement': [
                    {
                        'Item': 'Software',
                        'S/W version': 'B46-PfF132',
                        'H/W version': '-',
                        'Details': 'Optimized display driver algorithms to reduce flickering at 8K resolution'
                    }
                ]
            },
            {
                'Symptom': 'Display',
                'Case Code': 'P260309-03376/P260316-02536/P260316-07345',
                'Progr.Stat.': 'Resolve - Released',
                'Sub-Symptom': 'Flickering Google Pics',
                'Imp. Applied Date': datetime(2026, 3, 25).date(),
                'Improvement': [
                    {
                        'Item': 'Software',
                        'S/W version': 'B47-GpF155',
                        'H/W version': '-',
                        'Details': 'Fixed compatibility issue with Google Photos rendering engine'
                    }
                ]
            },
            {
                'Symptom': 'Application',
                'Case Code': 'P260316-09833',
                'Progr.Stat.': 'Resolve - Released',
                'Sub-Symptom': 'Transferred Video is not Playing Properly',
                'Imp. Applied Date': datetime(2026, 3, 25).date(),
                'Improvement': [
                    {
                        'Item': 'Software',
                        'S/W version': 'B48-VpF201',
                        'H/W version': '-',
                        'Details': 'Enhanced video codec support for transferred files'
                    }
                ]
            },
            {
                'Symptom': 'Appearance',
                'Case Code': 'Market Voc',
                'Progr.Stat.': 'Resolve – Process Improved',
                'Sub-Symptom': 'Dust on Camera',
                'Imp. Applied Date': datetime(2026, 3, 6).date(),
                'Improvement': [
                    {
                        'Item': 'Hardware',
                        'S/W version': '-',
                        'H/W version': 'Rev. C',
                        'Details': 'Added improved dust seals around camera module'
                    }
                ]
            },
            {
                'Symptom': 'Battery',
                'Case Code': 'Market Voc',
                'Progr.Stat.': 'Resolve – Training & OPL',
                'Sub-Symptom': 'Battery Swell',
                'Imp. Applied Date': datetime(2026, 3, 13).date(),
                'Improvement': [
                    {
                        'Item': 'Process',
                        'S/W version': '-',
                        'H/W version': '-',
                        'Details': 'Implemented new battery handling procedures in service centers'
                    }
                ]
            },
            {
                'Symptom': 'Display',
                'Case Code': 'P260317-07832',
                'Progr.Stat.': 'Resolve – Vendor Process Improved',
                'Sub-Symptom': 'Mung Display',
                'Imp. Applied Date': datetime(2026, 3, 19).date(),
                'Improvement': [
                    {
                        'Item': 'Hardware',
                        'S/W version': '-',
                        'H/W version': 'Rev. D',
                        'Details': 'Upgraded display panel supplier with improved QC standards'
                    }
                ]
            },
            {
                'Symptom': 'Camera',
                'Case Code': 'P260406-06627',
                'Progr.Stat.': 'Resolve – Vendor Process Improved',
                'Sub-Symptom': 'Spot on Camera',
                'Imp. Applied Date': datetime(2026, 3, 18).date(),
                'Improvement': [
                    {
                        'Item': 'Hardware',
                        'S/W version': '-',
                        'H/W version': 'Rev. B',
                        'Details': 'Added protective film during assembly to prevent dust ingress'
                    }
                ]
            },
            {
                'Symptom': 'Camera',
                'Case Code': 'P260414-02941',
                'Progr.Stat.': 'Resolve – Vendor Process Improved',
                'Sub-Symptom': 'Spot on Camera',
                'Imp. Applied Date': datetime(2026, 3, 18).date(),
                'Improvement': [
                    {
                        'Item': 'Process',
                        'S/W version': '-',
                        'H/W version': '-',
                        'Details': 'Implemented new cleaning protocol for camera lenses before assembly'
                    }
                ]
            }
        ]
        st.session_state.df_improvement = data

    @st.cache_data
    def get_unique_symptoms(data):
        return list(set(item['Symptom'] for item in data))

    # Create selectbox
    unique_symptoms = get_unique_symptoms(st.session_state.df_improvement)
    c1,c2 = st.columns([1,6])
    with c1:
        selected_symptom = st.selectbox(
            "Symptom",
            options=['All'] + unique_symptoms,
            index=0
        )

    # Filter and display
    if selected_symptom == 'All':
        df = pd.DataFrame(st.session_state.df_improvement)
    else:
        filtered_data = [item for item in st.session_state.df_improvement if item['Symptom'] == selected_symptom]
        df = pd.DataFrame(filtered_data)

    def format_improvement(improvement_list):
        formatted = []
        for item in improvement_list:
            text = (
                f"<div style='text-align: left;'>"
                f"<b>Item:</b> {item['Item']}<br>"
                f"<b>S/W version:</b> {item['S/W version']}<br>"
                f"<b>H/W version:</b> {item['H/W version']}<br>"
                f"<b>Details:</b> {item['Details']}"
                f"</div>"
            )
            formatted.append(text)
        return "<br><br>".join(formatted)

    # Apply formatting to the Improvement column
    df['Improvement'] = df['Improvement'].apply(format_improvement)
    df.insert(0, 'S.No.', range(1, len(df) + 1))

    html_table = df.to_html(
        index=False,
        classes="improvement-table",
        escape=False,
        border=0
    )

    # Inject custom CSS for column sizing
    custom_css = """
    <style>
    .improvement-table {
      width: 100% !important;
      table-layout: fixed !important;
    }
    .improvement-table th {
      background-color: #dbeafe !important;
      text-align: center !important;
    }
    .improvement-table td {
      text-align: center !important;
      word-wrap: break-word !important;
    }

    /* Column width adjustments */
    .improvement-table th:nth-child(1),
    .improvement-table td:nth-child(1) {
        width: 5% !important;
    }
    .improvement-table th:nth-child(2),
    .improvement-table td:nth-child(2) {
        width: 10% !important;
    }
    .improvement-table th:nth-child(3),
    .improvement-table td:nth-child(3) {
        width: 15% !important;
    }
    .improvement-table th:nth-child(4),
    .improvement-table td:nth-child(4) {
        width: 15% !important;
    }
    .improvement-table th:nth-child(5),
    .improvement-table td:nth-child(5) {
        width: 15% !important;
    }
    .improvement-table th:nth-child(6),
    .improvement-table td:nth-child(6) {
        width: 10% !important;
    }
    .improvement-table th:nth-child(7),
    .improvement-table td:nth-child(7) {
        width: 30% !important;
    }
    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown(html_table, unsafe_allow_html=True)

    if 'show_form' not in st.session_state:
        st.session_state.show_form = False
        st.session_state.form_improvements = [{
            'Item': '',
            'S/W version': '',
            'H/W version': '',
            'Details': ''
        }]

    # Button to toggle form visibility
    if st.button("Add New Improvement", type="primary"):
        st.session_state.show_form = not st.session_state.show_form

    # Display form if show_form is True
    if st.session_state.show_form:
        with st.form(key='improvement_form'):  # Create a form context
            st.title("Improvement Form")
            symptom_options = ["Display", "Application", "Appearance", "Battery", "Camera"]
            prog_stat_options = [
                "Resolve - Released",
                "Resolve – Process Improved",
                "Resolve – Training & OPL",
                "Resolve – Vendor Process Improved"
            ]

            # Form fields
            col1, col2 = st.columns(2)
            with col1:
                symptom = st.selectbox("Symptom*", options=symptom_options)
                sub_symptom = st.text_input("Sub-Symptom*", placeholder="e.g., Flickering 8K, Dust on Camera")

            with col2:
                case_code = st.text_input("Case Code*", placeholder="e.g., P260302-06393 or Market Voc")
                prog_stat = st.selectbox("Progress Status*", options=prog_stat_options)
                date = st.date_input("Imp. Applied Date*", value=datetime.today())

            # Improvement items section
            st.markdown(
                "<div style='text-align: left; font-weight: bold; font-size: 1.1em;'>Improvement Items</div>",
                unsafe_allow_html=True
            )
            for i, improvement in enumerate(st.session_state.form_improvements):
                cols = st.columns([2, 2, 2])
                with cols[0]:
                    item = st.selectbox("Item*", ["", "Software", "Hardware", "Process"],
                                        index=["Software", "Hardware", "Process"].index(improvement['Item']) + 1
                                        if improvement['Item'] in ["Software", "Hardware", "Process"] else 0,
                                        key=f"item_{i}")
                with cols[1]:
                    sw_version = st.text_input("S/W version", improvement['S/W version'],
                                               placeholder="Version", key=f"sw_{i}")
                with cols[2]:
                    hw_version = st.text_input("H/W version", improvement['H/W version'],
                                               placeholder="Parts", key=f"hw_{i}")
                details = st.text_area("Details*", improvement['Details'],
                                       placeholder="Description", key=f"details_{i}")
                # Update session state
                st.session_state.form_improvements[i] = {
                    'Item': item,
                    'S/W version': sw_version,
                    'H/W version': hw_version,
                    'Details': details
                }

            # Form buttons
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submit = st.form_submit_button("Submit")
            with col_cancel:
                cancel = st.form_submit_button("Cancel")  # Use form_submit_button for Cancel

            if cancel:
                st.session_state.show_form = False
                st.session_state.form_improvements = [{
                    'Item': '',
                    'S/W version': '',
                    'H/W version': '',
                    'Details': ''
                }]
                st.rerun()

            if submit:
                required_fields = [
                    case_code, prog_stat, symptom,
                    sub_symptom, date
                ]

                # Check if all improvement items are valid
                valid_improvements = all(
                    imp['Item'] and imp['Details']
                    for imp in st.session_state.form_improvements
                )

                if not all(required_fields):
                    st.warning("Please fill all required fields (*)!")
                elif not valid_improvements:
                    st.warning("Each improvement item requires at least 'Item' and 'Details'!")
                else:
                    new_entry = {
                        'Imp. Applied Date': date,
                        'Case Code': case_code,
                        'Progr.Stat.': prog_stat,
                        'Symptom': symptom,
                        'Sub-Symptom': sub_symptom,
                        'Improvement': st.session_state.form_improvements.copy()
                    }
                    st.session_state.df_improvement.append(new_entry)

                    st.success("Submitted Successfully!")
                    st.balloons()

                    # Reset form
                    st.session_state.show_form = False
                    st.session_state.form_improvements = [{
                        'Item': '',
                        'S/W version': '',
                        'H/W version': '',
                        'Details': ''
                    }]
                    st.rerun()
