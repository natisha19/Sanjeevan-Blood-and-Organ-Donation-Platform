import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
from datetime import date
import hashlib
import streamlit as st
import base64

# Load and encode image
def get_svg_base64(svg_file):
    with open(svg_file, "r", encoding="utf-8") as f:
        svg_data = f.read()
    # Encode SVG content to base64
    encoded_svg = base64.b64encode(svg_data.encode()).decode()
    return encoded_svg


st.set_page_config(page_title="Sanjeevan Donation System", layout="wide")

# ---------- DB CONNECT ----------
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None

def check_blood_compatibility(donor_bg, recipient_bg):
    # Blood type compatibility rules
    compatibility = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+']
    }
    return recipient_bg in compatibility.get(donor_bg, [])

# ---------- STYLING ----------
def set_svg_background(svg_file):
    svg_base64 = get_svg_base64(svg_file)
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/svg+xml;base64,{svg_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: fill;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def get_next_autoincrement_id(table_name):
    try:
        cursor.execute(f"SHOW TABLE STATUS WHERE Name = '{table_name}'")
        result = cursor.fetchone()
        return result['Auto_increment']
    except Exception as e:
        st.error(f"Error fetching next id for {table_name}: {e}")
        return None


set_svg_background("bgimgg.svg")
st.markdown("""
    <style>
    .main {
        background-color: rgba(255, 245, 245, 0.9);
    }

    

    /* Default Streamlit button override (keeps your existing primary look) */
    .stButton > button {
        background-color: #b30000;
        color: white;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5em 3em;
    }
    .stButton > button:hover {
        background-color: #ff4d4d;
    }

    /* Large variant if you want to target a "big" button you render as HTML */
    .stButton > button.bigbutton {
        background-color: #b30000;
        color: white;
        border-radius: 10px;
        font-weight: 600;
        padding: 1.2em 2.5em;
    }
    .stButton > button.bigbutton:hover {
        background-color: #ff4d4d;
    }

    /* Additional button types (for custom HTML buttons you can inject) */
    .custombtn {
        background-color: #b30000;
        color: white;
        border-radius: 10px;
        font-weight: 600;
        padding: 1.2em 2.5em;
    }

    /* Secondary (blue) */
    .custombtn:hover {
        background-color: #ff4d4d;
    }
    
    /* Keep custom buttons responsive inside Streamlit */
    .custombtns { margin: 8px 0 16px 0; }
            
    [data-testid="stSidebar"] {
    background-color: EB8888 !important;
    }
    input, textarea, select {
        border: 2px solid #aa3a2a !important;
        border-radius: 7px !important;
        padding: 8px !important;
    }
    [data-testid="stForm"] {
        border: 3px solid #aa3a2a !important;
        border-radius: 30px !important;
        padding: 25px !important;
    }
        
    </style>


    
    
""", unsafe_allow_html=True)



# Initialize session states
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = None

st.markdown(
    "<h1 style='text-align: center;'>SANJEEVAN</h1>" \
    "<h2 style='text-align: center;'>Blood & Organ Donation Management</h2>",
    unsafe_allow_html=True
)

# ---------- AUTHENTICATION FLOW ----------
if not st.session_state['authenticated']:
    if st.session_state['page'] == 'home':
        st.markdown("### Please login to continue")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Login as Admin", key="admin_login_btn"):
                st.session_state['page'] = 'admin_login'
        with col2:
            if st.button("Login as Hospital", key="hospital_login_btn"):
                st.session_state['page'] = 'hospital_login'
        with col3:
            if st.button("Register As Blood Donor", key="donorregisterbtn"):
                st.session_state.page = "donorregister"

        with col4:
            if st.button("Register As Blood Recipient", key="recipientregisterbtn"):
                st.session_state.page = "recipientregister"

        st.markdown("""
    <div style="width:900px; margin-top:60px; margin-left:5px; background-color:#ffecec; padding:15px 20px; border-radius:12px; border:2px solid #aa3a2a; font-size:1.12em;">
    <strong>Sanjeevan – Because Every Drop Counts, Every Life Matters

Welcome to Sanjeevan, an intelligent and compassionate platform designed to revolutionize blood and organ donation management.
Our mission is simple yet powerful to bridge the gap between donors, recipients, and hospitals through technology, transparency, and trust.

Sanjeevan brings together critical data from donor profiles and recipient needs to hospital coordination and compatibility tracking into one intuitive, secure interface.
With built-in smart validations, real-time updates, and a modern interface, it empowers medical professionals and volunteers alike to focus on what truly matters saving lives.
</div>
    """, unsafe_allow_html=True)
    
    elif st.session_state.page == "donorregister":
        st.markdown(
    "<h3 style='text-align: center;'>Register As Blood Donor</h3>",
    unsafe_allow_html=True
)
         
        conn = get_connection()
        if not conn:
            st.stop()

        cursor = conn.cursor(dictionary=True)
        st.markdown('<div style="max-width:400px;margin:auto;">', unsafe_allow_html=True)
        next_donor_id = get_next_autoincrement_id('donor')
        with st.form("donor_registration_form"):
            donor_id = st.text_input("Donor ID", value=str(next_donor_id), disabled=True)
            first_name = st.text_input("First Name")
            middle_name = st.text_input("Middle Name (Optional)")
            last_name = st.text_input("Last Name")
            dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            contact_number = st.text_input("Contact Number")
            hospital_id = st.number_input("Hospital ID", min_value=1, step=1)
            donation_type = st.selectbox("Donation Type", ['Blood'], key="donation_type")
            submitted = st.form_submit_button("Register Donor")
            

            if submitted:
                    if not last_name.strip():
                        st.error("⚠️ Last Name is mandatory. Please enter it before proceeding.")
                    else:
                        try:
                            query = """
                            INSERT INTO Donor (Donor_ID, First_Name, Middle_Name, Last_Name, DOB, Gender, Blood_Group, Contact_Number, Hospital_ID, Donation_Type)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """
                            cursor.execute(query, (donor_id, first_name, middle_name, last_name, dob, gender, blood_group, contact_number, hospital_id, donation_type))
                            conn.commit()
                            st.success("✅ Donor added successfully!")
                        except Error as e:
                            st.error(f"Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
            

    elif st.session_state.page == "recipientregister":
        st.header("Register As Blood Recipient")
        conn = get_connection()
        if not conn:
            st.stop()
        cursor = conn.cursor(dictionary=True)
        next_rec_id = get_next_autoincrement_id('recipient')
        with st.form("add_recipient_form"):
                rec_id = st.text_input("Recipient ID", value=str(next_rec_id), disabled=True)
                first = st.text_input("First Name")
                middle = st.text_input("Middle Name (Optional)")
                last = st.text_input("Last Name")
                dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                blood_group = st.selectbox("Blood Group", ['A+','A-','B+','B-','AB+','AB-','O+','O-'])
                contact = st.text_input("Contact Number")
                organ = st.selectbox("Required Organ", ['Blood'], key="required_organ")
                urgency = st.selectbox("Urgency Level", ['Low','Medium','High'])
                hospital_id = st.number_input("Hospital ID", step=1, min_value=1)
                submitted = st.form_submit_button("➕ Add Recipient")

                if submitted:
                    if not last.strip():
                        st.error("⚠️ Last Name is mandatory. Please enter it before proceeding.")
                    else:
                        try:
                            query = """
                            INSERT INTO Recipient (Recipient_ID, First_Name, Middle_Name, Last_Name, DOB, Gender, Blood_Group, Contact_Number, Required_Organ, Urgency_Level, Hospital_ID)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """
                            cursor.execute(query, (rec_id, first, middle, last, dob, gender, blood_group, contact, organ, urgency, hospital_id))
                            conn.commit()
                            st.success("✅ Recipient added successfully!")
                        except Error as e:
                            st.error(f"Error: {e}")

    
    elif st.session_state['page'] == 'admin_login':
        st.header("Admin Login")
        login_mode = st.radio("Select Mode", ["Login", "Create Account"])
        
        if login_mode == "Login":
            with st.form("admin_login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    conn = get_connection()
                    if not conn:
                        st.stop()
                    cursor = conn.cursor(dictionary=True)
                    
                    hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute("SELECT * FROM admin_users WHERE username = %s AND password = %s", 
                                 (username, hashed_pwd))
                    admin = cursor.fetchone()
                    
                    if admin:
                        st.session_state['authenticated'] = True
                        st.session_state['user_type'] = 'admin'
                        st.session_state['user_id'] = admin['id']
                        st.session_state['page'] = 'main'
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                    
                    cursor.close()
                    conn.close()
        
        else:  # Create Account
            with st.form("admin_signup_form"):
                new_username = st.text_input("Choose Username")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account")
                
                if submitted:
                    if new_password != confirm_password:
                        st.error("Passwords don't match!")
                    else:
                        conn = get_connection()
                        if not conn:
                            st.stop()
                        cursor = conn.cursor(dictionary=True)
                        
                        try:
                            hashed_pwd = hashlib.sha256(new_password.encode()).hexdigest()
                            cursor.execute("INSERT INTO admin_users (username, password) VALUES (%s, %s)",
                                         (new_username, hashed_pwd))
                            conn.commit()
                            st.success("Account created successfully! You can now login.")
                        except Error as e:
                            if "Duplicate entry" in str(e):
                                st.error("Username already exists!")
                            else:
                                st.error(f"Error: {e}")
                        finally:
                            cursor.close()
                            conn.close()
    
    elif st.session_state['page'] == 'hospital_login':
        st.header("Hospital Login")
        login_mode = st.radio("Select Mode", ["Login", "Register Hospital"])
        
        if login_mode == "Login":
            with st.form("hospital_login_form"):
                hospital_id = st.number_input("Hospital ID", min_value=1, step=1)
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    conn = get_connection()
                    if not conn:
                        st.stop()
                    cursor = conn.cursor(dictionary=True)
                    
                    hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute("""
                        SELECT h.*, ha.password 
                        FROM Hospital h
                        JOIN hospital_auth ha ON h.Hospital_ID = ha.hospital_id
                        WHERE h.Hospital_ID = %s AND ha.password = %s
                    """, (hospital_id, hashed_pwd))
                    hospital = cursor.fetchone()
                    
                    if hospital:
                        st.session_state['authenticated'] = True
                        st.session_state['user_type'] = 'hospital'
                        st.session_state['hospital_id'] = hospital_id
                        st.session_state['hospital_name'] = hospital['Name']
                        st.session_state['page'] = 'main'
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                    
                    cursor.close()
                    conn.close()
        
        else:  # Register Hospital
            with st.form("hospital_register_form"):
                st.subheader("Hospital Registration")
                # Hospital details
                new_hospital_id = st.number_input("Hospital ID", min_value=1, step=1)
                hospital_name = st.text_input("Hospital Name")
                hospital_location = st.text_input("Hospital Location")
                hospital_contact = st.text_input("Contact Number")
                
                # Authentication details
                st.subheader("Set Login Credentials")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                submitted = st.form_submit_button("Register Hospital")
                
                if submitted:
                    if not hospital_name.strip() or not hospital_location.strip():
                        st.error("Hospital Name and Location are required!")
                    elif new_password != confirm_password:
                        st.error("Passwords don't match!")
                    else:
                        conn = get_connection()
                        if not conn:
                            st.stop()
                        cursor = conn.cursor(dictionary=True)
                        
                        try:
                            # Start transaction
                            conn.start_transaction()
                            
                            # Check if hospital ID already exists
                            cursor.execute("SELECT * FROM Hospital WHERE Hospital_ID = %s", (new_hospital_id,))
                            if cursor.fetchone():
                                st.error("Hospital ID already exists!")
                                conn.rollback()
                            else:
                                # First insert into Hospital table
                                cursor.execute("""
                                    INSERT INTO Hospital (Hospital_ID, Name, Location, Contact)
                                    VALUES (%s, %s, %s, %s)
                                """, (new_hospital_id, hospital_name, hospital_location, hospital_contact))
                                
                                # Then create authentication credentials
                                hashed_pwd = hashlib.sha256(new_password.encode()).hexdigest()
                                cursor.execute("""
                                    INSERT INTO hospital_auth (hospital_id, password)
                                    VALUES (%s, %s)
                                """, (new_hospital_id, hashed_pwd))
                                
                                conn.commit()
                                st.success("Hospital registered successfully! You can now login.")
                                
                        except Error as e:
                            conn.rollback()
                            st.error(f"Error: {e}")
                        finally:
                            cursor.close()
                            conn.close()

# ---------- MAIN APPLICATION (Only shown after authentication) ----------
else:
    # Add logout button in sidebar
    if st.sidebar.button("Logout", key="main_logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    
    # Show user info in sidebar
    if st.session_state['user_type'] == 'admin':
        st.sidebar.info(f"Logged in as Admin")
    else:
        st.sidebar.info(f"Logged in as Hospital: {st.session_state['hospital_name']}")
    
    # Different navigation options based on user type
    if st.session_state['user_type'] == 'hospital':
        menu = st.sidebar.radio("Navigate", ["Organ Compatibility Confirmations", "Events"])  # Single page for hospitals
    else:
        menu = st.sidebar.radio("Navigate", ["Home", "Manage Donors", "Manage Recipients", "Compatibility", "Events"])

    # Handle different menu options
    if menu == "Organ Compatibility Confirmations":
        st.title(f"Organ Compatibility Confirmations - {st.session_state['hospital_name']}")
        
        conn = get_connection()
        if not conn:
            st.stop()
        cursor = conn.cursor(dictionary=True)

        # Initialize session state for compatibility check
        if 'compatibility_step' not in st.session_state:
            st.session_state.compatibility_step = 'select'
            st.session_state.blood_compatible = False
            
        # Tab for new compatibility check
        tab1, tab2 = st.tabs(["New Compatibility Check", "View Compatibility History"])
        
        with tab1:
            st.header("Record New Compatibility")
            # Get donors from this hospital
            cursor.execute("""
                SELECT d.Donor_ID, 
                       CONCAT(d.First_Name, ' ', d.Last_Name, ' (Blood Group: ', d.Blood_Group, ')') as Name
                FROM Donor d
                WHERE d.Donation_Type IN ('Blood and Organ', 'Organ')
            """)
            donors = cursor.fetchall()
            
            # Get recipients from this hospital
            cursor.execute("""
                SELECT r.Recipient_ID, 
                       CONCAT(r.First_Name, ' ', r.Last_Name, 
                             ' (Blood Group: ', r.Blood_Group,
                             ', Needs: ', r.Required_Organ, ')') as Name
                FROM Recipient r
                WHERE r.Hospital_ID = %s
            """, (st.session_state['hospital_id'],))
            recipients = cursor.fetchall()
            
            # Create donor and recipient options
            donor_options = {"Select Donor": 0}
            donor_options.update({d['Name']: d['Donor_ID'] for d in donors})
            
            recipient_options = {"Select Recipient": 0}
            recipient_options.update({r['Name']: r['Recipient_ID'] for r in recipients})
            
            # First form for selection
            # Step 1: Selection form
            if "compatibility_step" not in st.session_state:
                st.session_state.compatibility_step = "select"
                
            if st.session_state.compatibility_step == "select":
                with st.form("compatibility_check"):
                    col1, col2 = st.columns(2)
                    with col1:
                        donor_name = st.selectbox("Select Donor", 
                                               options=list(donor_options.keys()),
                                               key="donor_select")
                        donor_id = donor_options[donor_name]
                    
                    with col2:
                        recipient_name = st.selectbox("Select Recipient",
                                                   options=list(recipient_options.keys()),
                                                   key="recipient_select")
                        recipient_id = recipient_options[recipient_name]
                    
                    check_compatibility = st.form_submit_button("Check Compatibility", use_container_width=True)

                if check_compatibility and donor_id > 0 and recipient_id > 0:
                    # Store the selected IDs in session state
                    st.session_state.selected_donor_id = donor_id
                    st.session_state.selected_recipient_id = recipient_id
                    st.session_state.compatibility_step = "record"
                    st.rerun()

            # Step 2: Record compatibility
            if st.session_state.compatibility_step == "record":
                donor_id = st.session_state.selected_donor_id
                recipient_id = st.session_state.selected_recipient_id
                
                # Get detailed information
                cursor.execute("""
    SELECT 
        d.First_Name AS donor_name,
        d.Blood_Group AS donor_bg,
        r.First_Name AS recipient_name,
        r.Blood_Group AS recipient_bg,
        r.Required_Organ AS required_organ
    FROM Donor d, Recipient r
    WHERE d.Donor_ID = %s AND r.Recipient_ID = %s
""", (donor_id, recipient_id))

                match = cursor.fetchone()

                if match:
                    st.info("### Compatibility Information")
                    st.write(f"**Donor:** {match['donor_name']} (Blood Group: {match['donor_bg']})")
                    st.write(f"**Recipient:** {match['recipient_name']} (Blood Group: {match['recipient_bg']})")
                    st.write(f"**Required Organ:** {match['required_organ']}")

                    # Blood compatibility check
                    blood_compatible = check_blood_compatibility(match['donor_bg'], match['recipient_bg'])
                    
                    # Store compatibility result in session state
                    st.session_state.blood_compatible = blood_compatible
                    
                    # # Show appropriate message based on compatibility
                    # if blood_compatible:
                    #     st.success("✅ Blood groups are compatible!")
                    # else:
                    #     st.error("❌ Blood groups are not compatible!")
                    #     st.warning("Cannot proceed with organ compatibility check.")
                        
                    # Only show compatibility form if blood groups are compatible
                    if blood_compatible:
                    
                        # Blood compatibility check results
                        blood_compatible = check_blood_compatibility(match['donor_bg'], match['recipient_bg'])
                        
                        if not blood_compatible:
                            st.error("❌ Blood groups are not compatible!")
                            st.warning("Cannot proceed with organ compatibility check.")
                        else:
                            st.success("✅ Blood groups are compatible!")
                            # Form for compatibility status
                            with st.form("record_compatibility_form"):
                                status = st.radio("Confirm Final Compatibility Status",
                                                ["Compatible", "Not Compatible"])
                                compatibility_score = st.number_input(
                                    "Compatibility Score (0-100)",
                                    min_value=0,
                                    max_value=100,
                                    value=100 if status == "Compatible" else 0,
                                    step=1,
                                    help="Enter a numeric compatibility score to store with this compatibility record."
                                )
                                submitted_record = st.form_submit_button("Record Compatibility Status", use_container_width=True)
                            
                            if submitted_record:
                                try:
                                    # Insert into Organ_Compatibility
                                    insert_query = """
                                        INSERT INTO Organ_Compatibility 
                                        (Donor_ID, Recipient_ID, Match_Status, 
                                        Compatibility_Score)
                                        VALUES (%s, %s, %s, %s)
                                    """
                                    values = (
                                        donor_id, recipient_id, 
                                        'Compatible' if status == 'Compatible' else 'Not Compatible',
                                        compatibility_score
                                    )
                                    cursor.execute(insert_query, values)
                                    
                                    # If status is Compatible, create an Organ Donation Event
                                    if status == "Compatible":
                                        cursor.execute("""
                                            INSERT INTO Organ_Donation_Event 
                                            (Donor_ID, Recipient_ID, Organ_Matched, Date)
                                            VALUES (%s, %s, %s, CURDATE())
                                        """, (donor_id, recipient_id, match['required_organ']))
                                    
                                    conn.commit()
                                    st.success("✅ Compatibility status recorded successfully!")
                                    if status == "Compatible":
                                        st.success("✅ Organ donation event created!")                                    # Reset to selection step
                                        st.session_state.compatibility_step = "select"
                                        st.rerun()
                                        
                                except Error as e:
                                    conn.rollback()
                                    st.error(f"Error recording status: {e}")
                                    st.error("Please try again or contact support if the error persists.")
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"An unexpected error occurred: {e}")
                    else:

                        st.warning("Cannot proceed with organ compatibility check.")
                        st.session_state.compatibility_step = "select"
                        st.rerun()
            # Navigation controls: go back to selection or clear the form and start over
            col_back, col_clear = st.columns(2)
            with col_back:
                if st.button("Back to Selection", key="back_to_selection"):
                    st.session_state.compatibility_step = "select"
                    st.rerun()

    
                        
    
        with tab2:
            st.header("Compatibility History")
            # View existing compatibility records
            # First check if the hospital has any donors and recipients
            cursor.execute("SELECT COUNT(*) as count FROM Donor WHERE Hospital_ID = %s", 
                         (st.session_state['hospital_id'],))
            donor_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM Recipient WHERE Hospital_ID = %s", 
                         (st.session_state['hospital_id'],))
            recipient_count = cursor.fetchone()['count']
            
            if donor_count == 0:
                st.warning("No donors registered in your hospital yet.")
            elif recipient_count == 0:
                st.warning("No recipients registered in your hospital yet.")
            else:
                cursor.execute("""
                    SELECT 
                        oc.O_Compatibility_ID,
                        oc.Donor_ID,
                        oc.Recipient_ID,
                        CONCAT(d.First_Name, ' ', d.Last_Name) as Donor_Name,
                        CONCAT(r.First_Name, ' ', r.Last_Name) as Recipient_Name,
                        r.Required_Organ,
                        oc.Match_Status,
                        oc.Compatibility_Score,
                        d.Blood_Group as Donor_Blood_Group,
                        r.Blood_Group as Recipient_Blood_Group,
                        d.Hospital_ID
                    FROM Organ_Compatibility oc
                    JOIN Donor d ON oc.Donor_ID = d.Donor_ID
                    JOIN Recipient r ON oc.Recipient_ID = r.Recipient_ID
                    WHERE d.Hospital_ID = %s
                    ORDER BY oc.O_Compatibility_ID DESC
                """, (st.session_state['hospital_id'],))
                
                history = cursor.fetchall()
                if history:
                    df = pd.DataFrame(history)
                    st.table(
    df.style.set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#aa3a2a'), ('color', '#ffcaca')]}
    ]).set_properties(**{
        'background-color': "#ffecec53", 
        'color': '#2c2c2c',
        'font-family': 'arial'
    })
)
                else:
                    st.info("No compatibility checks recorded yet for your hospital.")

        cursor.close()
        conn.close()
    
    # ---------- HOME ----------
    if menu == "Home":
        st.markdown("""
        ## 🏥 Sanjeevan Admin Dashboard

        Welcome, **Administrator** 👋  
        You are managing the Sanjeevan Blood & Organ Donation System a unified platform that connects hospitals, donors, and recipients to streamline life-saving donations.
        """)

        conn = get_connection()
        if not conn:
            st.stop()
        cursor = conn.cursor(dictionary=True)

        st.subheader("🏥 Registered Hospitals")

        # Display all hospital records
        cursor.execute("SELECT * FROM Hospital")
        hospitals = cursor.fetchall()

        if hospitals:
            df = pd.DataFrame(hospitals)
            st.table(
                df.style.set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#aa3a2a'), ('color', '#ffcaca')]}
                ]).set_properties(**{
                    'background-color': "#ffecec53",
                    'color': '#2c2c2c',
                    'font-family': 'arial'
                })
            )
        else:
            st.info("No hospitals registered yet.")

        # ---------- Hospital Management Actions ----------
        st.subheader("⚙️ Manage Hospitals")
        action = st.radio("Select Action", ["Add Hospital", "Update Hospital", "Delete Hospital"], horizontal=True)

        # ✅ Add Hospital
        if action == "Add Hospital":
            st.markdown("### ➕ Add New Hospital")
            with st.form("add_hospital_form"):
                hospital_id = st.number_input("Hospital ID", min_value=1, step=1)
                name = st.text_input("Hospital Name")
                location = st.text_input("Location")
                contact = st.text_input("Contact Number")

                submitted = st.form_submit_button("Add Hospital")

                if submitted:
                    if not name.strip():
                        st.error("⚠️ Hospital name cannot be empty.")
                    else:
                        try:
                            cursor.execute("""
                                INSERT INTO Hospital (Hospital_ID, Name, Location, Contact)
                                VALUES (%s, %s, %s, %s)
                            """, (hospital_id, name, location, contact))
                            conn.commit()
                            st.success(f"✅ Hospital '{name}' added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error adding hospital: {e}")

        # ✅ Update Hospital
        elif action == "Update Hospital":
            st.markdown("### ✏️ Update Hospital Details")

            if "loaded_hospital" not in st.session_state:
                st.session_state.loaded_hospital = None

            hospital_id = st.number_input("Enter Hospital ID to update", min_value=1, step=1)

            if st.button("🔍 Load Hospital"):
                cursor.execute("SELECT * FROM Hospital WHERE Hospital_ID = %s", (hospital_id,))
                hosp = cursor.fetchone()

                if hosp:
                    st.session_state.loaded_hospital = hosp
                    st.success(f"✅ Hospital ID {hospital_id} loaded successfully.")
                else:
                    st.session_state.loaded_hospital = None
                    st.warning("⚠️ No hospital found with that ID.")

            # If a hospital is loaded, show editable form
            if st.session_state.loaded_hospital:
                h = st.session_state.loaded_hospital

                with st.form("update_hospital_form"):
                    name = st.text_input("Hospital Name", value=h["Name"])
                    location = st.text_input("Location", value=h["Location"])
                    contact = st.text_input("Contact Number", value=h["Contact"])

                    submitted = st.form_submit_button("💾 Update Hospital")

                    if submitted:
                        try:
                            cursor.execute("""
                                UPDATE Hospital
                                SET Name = %s, Location = %s, Contact = %s
                                WHERE Hospital_ID = %s
                            """, (name, location, contact, hospital_id))
                            conn.commit()
                            st.success(f"✅ Hospital ID {hospital_id} updated successfully!")
                            st.session_state.loaded_hospital = None  # clear after update
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error updating hospital: {e}")


        # ✅ Delete Hospital
        elif action == "Delete Hospital":
            st.markdown("### 🗑️ Delete Hospital")
            hospital_id = st.number_input("Enter Hospital ID to delete", min_value=1, step=1)

            if st.button("Delete Hospital"):
                try:
                    # Prevent deletion if linked to donors or recipients
                    cursor.execute("""
                        SELECT 
                            (SELECT COUNT(*) FROM Donor WHERE Hospital_ID = %s) +
                            (SELECT COUNT(*) FROM Recipient WHERE Hospital_ID = %s)
                        AS linked_records;
                    """, (hospital_id, hospital_id))
                    count = cursor.fetchone()['linked_records']

                    if count > 0:
                        st.error(f"⚠️ Cannot delete Hospital ID {hospital_id} — it has {count} linked donors/recipients.")
                    else:
                        cursor.execute("DELETE FROM Hospital WHERE Hospital_ID = %s", (hospital_id,))
                        conn.commit()
                        st.success("✅ Hospital deleted successfully!")
                        st.rerun()

                except Exception as e:
                    st.error(f"❌ Error deleting hospital: {e}")

        cursor.close()
        conn.close()



    # ---------- DONORS ----------
    elif menu == "Manage Donors":
        st.header("Donor Management")
        conn = get_connection()
        if not conn:
            st.stop()

        cursor = conn.cursor(dictionary=True)

        action = st.radio("Select Action", ["View All Donors", "Add Donor", "Delete Donor", "Update Donor"])

        if action == "View All Donors":
            cursor.execute("""
                                SELECT Donor_ID, First_Name, Last_Name, Blood_Group, 
                                    Calculate_Age(DOB) AS Age, Gender, Donation_Type, Hospital_ID
                                FROM Donor
                            """)

            donors = cursor.fetchall()
            st.markdown("#### Calculate_Age Function used here to compute age from DOB.")
            df = pd.DataFrame(donors)
            st.table(
                        df.style.set_table_styles([
                            {'selector': 'th', 'props': [('background-color', '#aa3a2a'), ('color', '#ffcaca')]}
                        ]).set_properties(**{
                            'background-color': "#ffecec53", 
                            'color': '#2c2c2c',
                            'font-family': 'arial'
                        })
                    )

        st.subheader("🔍 Donors Older than Average Age")
        st.markdown("#### 📊 Aggregate (AVG) and Nested Query used here to find donors older than average age.")


        if st.button("Show Query Result"):
            try:
                cursor.execute("""
                    SELECT Donor_ID, First_Name, Last_Name, DOB
                    FROM Donor
                    WHERE Calculate_Age(DOB) > (
                        SELECT AVG(Calculate_Age(DOB))
                        FROM Donor
                    )
                """)
                result = cursor.fetchall()
                
                if result:
                    
                    df_nested = pd.DataFrame(result)
                    st.table(df_nested)
                    st.success("✅ Nested query+Aggregate executed successfully!")
                else:
                    st.info("No donor older than average found.")
            
            except Exception as e:
                st.error(f"Error executing nested query: {e}")


        elif action == "Add Donor":
            next_donor_id = get_next_autoincrement_id('donor')
            with st.form("add_donor_form"):
                donor_id = st.text_input("Donor ID", value=str(next_donor_id), disabled=True)
                first = st.text_input("First Name")
                middle = st.text_input("Middle Name (Optional)")
                last = st.text_input("Last Name")
                dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                blood_group = st.selectbox("Blood Group", ['A+','A-','B+','B-','AB+','AB-','O+','O-'])
                donation_type = st.selectbox("Donation Type", ['Blood', 'Organ', 'Blood and Organ'], help="Select what the donor wishes to donate")
                contact = st.text_input("Contact Number")
                hospital_id = st.number_input("Hospital ID", step=1, min_value=1)
                submitted = st.form_submit_button("➕ Add Donor")

                if submitted:
                    if not last.strip():
                        st.error("⚠️ Last Name is mandatory. Please enter it before proceeding.")
                    else:
                        try:
                            query = """
                            INSERT INTO Donor (Donor_ID, First_Name, Middle_Name, Last_Name, DOB, Gender, Blood_Group, Contact_Number, Hospital_ID, Donation_Type)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """
                            cursor.execute(query, (donor_id, first, middle, last, dob, gender, blood_group, contact, hospital_id, donation_type))
                            conn.commit()
                            st.success("✅ Donor added successfully!")
                        except Error as e:
                            st.error(f"Error: {e}")

        elif action == "Delete Donor":
            st.subheader("🗑️ Delete Donor Record")

            donor_id = st.number_input("Enter Donor ID to delete", step=1)

            if st.button("🗑️ Delete Donor"):
                # --- Step 1: Check dependencies ---
                cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM blood_compatibility WHERE Donor_ID = %s) +
                        (SELECT COUNT(*) FROM organ_compatibility WHERE Donor_ID = %s) +
                        (SELECT COUNT(*) FROM blood_donation_event WHERE Donor_ID = %s) +
                        (SELECT COUNT(*) FROM organ_donation_event WHERE Donor_ID = %s)
                    AS linked_records;
                """, (donor_id, donor_id, donor_id, donor_id))

                count = cursor.fetchone()['linked_records']

                if count > 0:
                    st.error(f"⚠️ Cannot delete Donor ID {donor_id} — Donor is linked to {count} record(s) in other tables.")
                else:
                    try:
                        cursor.execute("DELETE FROM donor WHERE Donor_ID = %s", (donor_id,))
                        conn.commit()
                        st.success(f"✅ Donor ID {donor_id} deleted successfully (no dependencies).")
                    except Exception as e:
                        st.error(f"❌ Error deleting donor: {e}")

        
        elif action == "Update Donor":
            st.header("Update Donor")
            load_id = st.number_input("Donor ID to load", step=1, min_value=1, key="load_donor_id")

            if st.button("🔎 Load Donor"):
                cursor.execute("SELECT * FROM Donor WHERE Donor_ID = %s", (load_id,))
                row = cursor.fetchone()
                if not row:
                    st.error("No donor found with that ID.")
                    if "loaded_donor" in st.session_state:
                        del st.session_state["loaded_donor"]
                else:
                    st.session_state["loaded_donor"] = row
                    st.success("Donor loaded. Edit fields below and submit to update.")

            if "loaded_donor" in st.session_state:
                r = st.session_state["loaded_donor"]

                def _index_or_default(lst, val, default=0):
                    try:
                        return lst.index(val)
                    except Exception:
                        return default

                gender_opts = ["Male", "Female", "Other"]
                bg_opts = ['A+','A-','B+','B-','AB+','AB-','O+','O-']
                donation_opts = ['Blood', 'Organ', 'Blood and Organ']

                with st.form("update_donor_form"):
                    first = st.text_input("First Name", value=r.get("First_Name", ""))
                    middle = st.text_input("Middle Name (Optional)", value=r.get("Middle_Name", ""))
                    last = st.text_input("Last Name", value=r.get("Last_Name", ""))
                    dob_val = r.get("DOB")
                    try:
                        dob = st.date_input("Date of Birth", value=dob_val if dob_val is not None else None)
                    except Exception:
                        dob = st.date_input("Date of Birth")
                    gender = st.selectbox("Gender", gender_opts, index=_index_or_default(gender_opts, r.get("Gender")))
                    blood_group = st.selectbox("Blood Group", bg_opts, index=_index_or_default(bg_opts, r.get("Blood_Group")))
                    contact = st.text_input("Contact Number", value=r.get("Contact_Number", ""))
                    hospital_id = st.number_input("Hospital ID", step=1, min_value=1, value=r.get("Hospital_ID", 1))
                    donation_type = st.selectbox("Donation Type", ['Blood', 'Organ', 'Blood and Organ'], index=_index_or_default(['Blood', 'Organ', 'Blood and Organ'], r.get("Donation_Type")))
                    submitted = st.form_submit_button("✏️ Update Donor")

                    if submitted:
                        if not str(last).strip():
                            st.error("⚠️ Last Name is mandatory. Please enter it before proceeding.")
                        else:
                            try:
                                update_query = """
                                    UPDATE Donor
                                    SET First_Name=%s, Middle_Name=%s, Last_Name=%s, DOB=%s, Gender=%s,
                                        Blood_Group=%s, Contact_Number=%s, Hospital_ID=%s, Donation_Type=%s
                                    WHERE Donor_ID=%s
                                """
                                cursor.execute(update_query, (
                                    first, middle, last, dob, gender,
                                    blood_group, contact, hospital_id, donation_type, r["Donor_ID"]
                                ))
                                conn.commit()
                                st.success("✅ Donor updated successfully!")
                                del st.session_state["loaded_donor"]
                            except Error as e:
                                st.error(f"Error: {e}")

        cursor.close()
        conn.close()

    # ---------- RECIPIENTS ----------
    elif menu == "Manage Recipients":
        st.header("Recipient Management")
        conn = get_connection()
        if not conn:
            st.stop()
        cursor = conn.cursor(dictionary=True)

        action = st.radio("Select Action", ["View All Recipients", "Add Recipient", "Delete Recipient", "Update Recipient"])

        if action == "View All Recipients":
            cursor.execute("""
                            SELECT Recipient_ID, First_Name, Middle_Name, Last_Name, Blood_Group, 
                                Calculate_Age(DOB) AS Age, Gender, Required_Organ, Urgency_Level, Hospital_ID
                            FROM Recipient
                        """)

            recips = cursor.fetchall()
            st.markdown("#### Calculate_Age Function used here to compute age from DOB.")
            df = pd.DataFrame(recips)
            st.table(
    df.style.set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#aa3a2a'), ('color', '#ffcaca')]}
    ]).set_properties(**{
        'background-color': "#ffecec53", 
        'color': '#2c2c2c',
        'font-family': 'arial'
    })
)

        elif action == "Add Recipient":
            next_rec_id = get_next_autoincrement_id('recipient')
            with st.form("add_recipient_form"):
                rec_id = st.text_input("Donor ID", value=str(next_rec_id), disabled=True)
                first = st.text_input("First Name")
                middle = st.text_input("Middle Name (Optional)")
                last = st.text_input("Last Name")
                dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                blood_group = st.selectbox("Blood Group", ['A+','A-','B+','B-','AB+','AB-','O+','O-'])
                contact = st.text_input("Contact Number")
                organ = st.text_input("Required Organ")
                urgency = st.selectbox("Urgency Level", ['Low','Medium','High'])
                hospital_id = st.number_input("Hospital ID", step=1, min_value=1)
                submitted = st.form_submit_button("➕ Add Recipient")

                if submitted:
                    if not last.strip():
                        st.error("⚠️ Last Name is mandatory. Please enter it before proceeding.")
                    else:
                        try:
                            query = """
                            INSERT INTO Recipient (Recipient_ID, First_Name, Middle_Name, Last_Name, DOB, Gender, Blood_Group, Contact_Number, Required_Organ, Urgency_Level, Hospital_ID)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            """
                            cursor.execute(query, (rec_id, first, middle, last, dob, gender, blood_group, contact, organ, urgency, hospital_id))
                            conn.commit()
                            st.success("✅ Recipient added successfully!")
                        except Error as e:
                            st.error(f"Error: {e}")

        elif action == "Delete Recipient":
            st.subheader("🗑️ Delete Recipient Record")

            rec_id = st.number_input("Enter Recipient ID to delete", step=1)

            if st.button("🗑️ Delete Recipient"):
                # --- Step 1: Check dependencies ---
                cursor.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM blood_compatibility WHERE Recipient_ID = %s) +
                        (SELECT COUNT(*) FROM organ_compatibility WHERE Recipient_ID = %s) +
                        (SELECT COUNT(*) FROM blood_donation_event WHERE Recipient_ID = %s) +
                        (SELECT COUNT(*) FROM organ_donation_event WHERE Recipient_ID = %s)
                    AS linked_records;
                """, (rec_id, rec_id, rec_id, rec_id))

                count = cursor.fetchone()['linked_records']

                if count > 0:
                    st.error(f"⚠️ Cannot delete Recipient ID {rec_id} — Recipient is linked to {count} record(s) in other tables.")
                else:
                    try:
                        cursor.execute("DELETE FROM recipient WHERE Recipient_ID = %s", (rec_id,))
                        conn.commit()
                        st.success(f"✅ Recipient ID {rec_id} deleted successfully (no dependencies).")
                    except Exception as e:
                        st.error(f"❌ Error deleting recipient: {e}")

        
        elif action == "Update Recipient":
            st.header("Update Recipient")
            load_id = st.number_input("Recipient ID to load", step=1, min_value=1, key="load_recipient_id")

            if st.button("🔎 Load Recipient"):
                cursor.execute("SELECT * FROM Recipient WHERE Recipient_ID = %s", (load_id,))
                row = cursor.fetchone()
                if not row:
                    st.error("No recipient found with that ID.")
                    if "loaded_recipient" in st.session_state:
                        del st.session_state["loaded_recipient"]
                else:
                    st.session_state["loaded_recipient"] = row
                    st.success("Recipient loaded. Edit fields below and submit to update.")

            if "loaded_recipient" in st.session_state:
                r = st.session_state["loaded_recipient"]

                def _index_or_default(lst, val, default=0):
                    try:
                        return lst.index(val)
                    except Exception:
                        return default

                gender_opts = ["Male", "Female", "Other"]
                bg_opts = ['A+','A-','B+','B-','AB+','AB-','O+','O-']
                urgency_opts = ['Low','Medium','High']

                with st.form("update_recipient_form"):
                    first = st.text_input("First Name", value=r.get("First_Name", ""))
                    middle = st.text_input("Middle Name (Optional)", value=r.get("Middle_Name", ""))
                    last = st.text_input("Last Name", value=r.get("Last_Name", ""))
                    dob_val = r.get("DOB")
                    try:
                        dob = st.date_input("Date of Birth", value=dob_val if dob_val is not None else None)
                    except Exception:
                        dob = st.date_input("Date of Birth")
                    gender = st.selectbox("Gender", gender_opts, index=_index_or_default(gender_opts, r.get("Gender")))
                    blood_group = st.selectbox("Blood Group", bg_opts, index=_index_or_default(bg_opts, r.get("Blood_Group")))
                    contact = st.text_input("Contact Number", value=r.get("Contact_Number", ""))
                    organ = st.text_input("Required Organ", value=r.get("Required_Organ", ""))
                    urgency = st.selectbox("Urgency Level", urgency_opts, index=_index_or_default(urgency_opts, r.get("Urgency_Level")))
                    hospital_id = st.number_input("Hospital ID", step=1, min_value=1, value=r.get("Hospital_ID", 1))
                    submitted = st.form_submit_button("✏️ Update Recipient")

                    if submitted:
                        if not str(last).strip():
                            st.error("⚠️ Last Name is mandatory. Please enter it before proceeding.")
                        else:
                            try:
                                update_query = """
                                    UPDATE Recipient
                                    SET First_Name=%s, Middle_Name=%s, Last_Name=%s, DOB=%s, Gender=%s,
                                        Blood_Group=%s, Contact_Number=%s, Required_Organ=%s, Urgency_Level=%s, Hospital_ID=%s
                                    WHERE Recipient_ID=%s
                                """
                                cursor.execute(update_query, (
                                    first, middle, last, dob, gender,
                                    blood_group, contact, organ, urgency, hospital_id, r["Recipient_ID"]
                                ))
                                conn.commit()
                                st.success("✅ Recipient updated successfully!")
                                del st.session_state["loaded_recipient"]
                            except Error as e:
                                st.error(f"Error: {e}")

        cursor.close()
        conn.close()

        # ---------- COMPATIBILITY ----------
    elif menu == "Compatibility":
        st.header("🔬 Compatibility Check")
        conn = get_connection()
        if not conn:
            st.stop()
        cursor = conn.cursor(dictionary=True)
        ctype = st.radio("Select Type", ["Blood Compatibility", "Organ Compatibility", "Record New Compatibility"])

        if ctype == "Blood Compatibility":
            cursor.execute("""
    SELECT 
        bc.Compatibility_ID,
        CONCAT(d.First_Name, ' ', d.Last_Name) AS Donor_Name,
        d.Blood_Group AS Donor_BloodGroup,
        CONCAT(r.First_Name, ' ', r.Last_Name) AS Recipient_Name,
        r.Blood_Group AS Recipient_BloodGroup,
        bc.Match_Status,
        bc.Compatibility_Score
    FROM blood_compatibility bc
    JOIN donor d ON bc.Donor_ID = d.Donor_ID
    JOIN recipient r ON bc.Recipient_ID = r.Recipient_ID
""")

            comp = cursor.fetchall()
            if comp:
                st.markdown("#### 🧩 This table uses a JOIN query between Donor, Recipient, and Blood_Compatibility tables.")

                df = pd.DataFrame(comp)
                st.table(
                            df.style.set_table_styles([
                                {'selector': 'th', 'props': [('background-color', '#aa3a2a'), ('color', '#ffcaca')]}
                            ]).set_properties(**{
                                'background-color': "#ffecec53", 
                                'color': '#2c2c2c',
                                'font-family': 'arial'
                            })
                        )
            else:
                st.info("No blood compatibility data found.")

        elif ctype == "Organ Compatibility":
            cursor.execute("""
        SELECT 
            oc.O_Compatibility_ID,
            CONCAT(d.First_Name, ' ', d.Last_Name) AS Donor_Name,
            d.Blood_Group AS Donor_BloodGroup,
            CONCAT(r.First_Name, ' ', r.Last_Name) AS Recipient_Name,
            r.Blood_Group AS Recipient_BloodGroup,
            r.Required_Organ AS Required_Organ,
            oc.Match_Status,
            oc.Compatibility_Score
        FROM organ_compatibility oc
        JOIN donor d ON oc.Donor_ID = d.Donor_ID
        JOIN recipient r ON oc.Recipient_ID = r.Recipient_ID
    """)
            comp = cursor.fetchall()
            if comp:
                st.markdown("#### 🧩 JOIN query used here between Organ_Compatibility, Donor, and Recipient tables.")
                df=pd.DataFrame(comp)
                st.table(
                    df.style.set_table_styles([
                        {'selector': 'th', 'props': [('background-color', '#aa3a2a'), ('color', '#ffcaca')]}
                    ]).set_properties(**{
                        'background-color': "#ffecec53", 
                        'color': '#2c2c2c',
                        'font-family': 'arial'
                    })
                )
            else:
                st.info("No organ compatibility data found.")
        
        # ✅ Recording New Compatibility
        elif ctype == "Record New Compatibility":
            st.subheader("🧬 Record New Compatibility")

            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # -----------------------------------------------------------
            # Step 1️⃣: Select Compatibility Type
            # -----------------------------------------------------------
            comp_type = st.radio("Select Compatibility Type to Record:", ["Blood Compatibility", "Organ Compatibility"])

            # -----------------------------------------------------------
            # Step 2️⃣: Load Donors & Recipients
            # -----------------------------------------------------------
            cursor.execute("""
                SELECT Donor_ID,
                    CONCAT(First_Name, ' ', Last_Name, ' (', Blood_Group, ')') AS Name
                FROM Donor
            """)
            donors = cursor.fetchall()

            if st.session_state['user_type'] == "hospital":
                cursor.execute("""
                    SELECT Recipient_ID,
                        CONCAT(First_Name, ' ', Last_Name,
                                ' (BG: ', Blood_Group, ', Need: ', Required_Organ, ')') AS Name
                    FROM Recipient
                    WHERE Hospital_ID = %s
                """, (st.session_state['hospital_id'],))
            else:
                cursor.execute("""
                    SELECT Recipient_ID,
                        CONCAT(First_Name, ' ', Last_Name,
                                ' (BG: ', Blood_Group, ', Need: ', Required_Organ, ')') AS Name
                    FROM Recipient
                """)
            recipients = cursor.fetchall()

            donor_options = {"Select Donor": 0}
            donor_options.update({d['Name']: d['Donor_ID'] for d in donors})

            recipient_options = {"Select Recipient": 0}
            recipient_options.update({r['Name']: r['Recipient_ID'] for r in recipients})

            # -----------------------------------------------------------
            # Step 3️⃣: Select Matching Pair
            # -----------------------------------------------------------
            if "comp_step" not in st.session_state:
                st.session_state.comp_step = "select"

            if st.session_state.comp_step == "select":
                with st.form("compatibility_pair_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        donor_name = st.selectbox("Select Donor", options=list(donor_options.keys()))
                        donor_id = donor_options[donor_name]
                    with col2:
                        recipient_name = st.selectbox("Select Recipient", options=list(recipient_options.keys()))
                        recipient_id = recipient_options[recipient_name]

                    proceed = st.form_submit_button("Proceed", use_container_width=True)
                    if proceed and donor_id > 0 and recipient_id > 0:
                        st.session_state.donor_id = donor_id
                        st.session_state.recipient_id = recipient_id
                        st.session_state.comp_step = "record"
                        st.session_state.comp_type = comp_type
                        st.rerun()
                    elif proceed:
                        st.warning("Please select both donor and recipient to continue.")

            # -----------------------------------------------------------
            # Step 4️⃣: Record Compatibility
            # -----------------------------------------------------------
            elif st.session_state.comp_step == "record":
                donor_id = st.session_state.donor_id
                recipient_id = st.session_state.recipient_id
                comp_type = st.session_state.comp_type

                cursor.execute("""
                    SELECT d.First_Name AS donor_name, d.Blood_Group AS donor_bg,
                        r.First_Name AS recipient_name, r.Blood_Group AS recipient_bg,
                        r.Required_Organ AS required_organ
                    FROM Donor d, Recipient r
                    WHERE d.Donor_ID = %s AND r.Recipient_ID = %s
                """, (donor_id, recipient_id))
                match = cursor.fetchone()

                if not match:
                    st.error("Invalid donor or recipient selected.")
                    st.session_state.comp_step = "select"
                    st.stop()

                st.info(f"**Donor:** {match['donor_name']} ({match['donor_bg']})")
                st.info(f"**Recipient:** {match['recipient_name']} ({match['recipient_bg']})")
                st.info(f"**Required Organ:** {match['required_organ']}")

                blood_ok = check_blood_compatibility(match['donor_bg'], match['recipient_bg'])

                if not blood_ok:
                    st.error("❌ Blood groups not compatible — cannot proceed.")
                    st.session_state.comp_step = "select"
                    st.stop()
                else:
                    st.success("✅ Blood groups compatible (Python verification passed).")

                # -------------------------------------------------------
                # BLOOD COMPATIBILITY RECORDING
                # -------------------------------------------------------
                if comp_type == "Blood Compatibility":
                    try:
                        # Check if record exists
                        cursor.execute("""
                            SELECT COUNT(*) AS cnt
                            FROM blood_compatibility
                            WHERE Donor_ID=%s AND Recipient_ID=%s
                        """, (donor_id, recipient_id))
                        exists = cursor.fetchone()['cnt']

                        if exists == 0:
                            st.info("🧩 Calling Stored Procedure sp_generate_blood_compatibility() ...")
                            cursor.execute(f"CALL sp_generate_blood_compatibility({donor_id}, {recipient_id});")
                            conn.commit()
                            st.success("✅ Stored Procedure executed successfully → fn_is_blood_compatible() used internally.")
                        else:
                            st.warning("ℹ Compatibility already exists — procedure skipped.")
                    except Exception as e:
                        st.error(f"❌ Procedure Error: {e}")

                # -------------------------------------------------------
                # ORGAN COMPATIBILITY RECORDING
                # -------------------------------------------------------
                elif comp_type == "Organ Compatibility":
                    with st.form("organ_comp_form"):
                        status = st.radio("Compatibility Status", ["Compatible", "Not Compatible"])
                        score = st.number_input("Compatibility Score", 0, 100, value=100 if status == "Compatible" else 0)
                        save = st.form_submit_button("Save Organ Compatibility")

                        if save:
                            try:
                                cursor.execute("""
                                    INSERT INTO organ_compatibility (Donor_ID, Recipient_ID, Match_Status, Compatibility_Score)
                                    VALUES (%s, %s, %s, %s)
                                """, (donor_id, recipient_id, status, score))
                                conn.commit()
                                st.success("✅ Organ Compatibility record saved successfully!")
                            except Exception as e:
                                st.error(f"❌ Error saving record: {e}")

                    # ---------------------------------------------------
                    # Trigger Demonstration for Organ_Donation_Event
                    # ---------------------------------------------------
                    st.markdown("##### Test Trigger: prevent_incompatible_organ_donation")
                    if st.button("Attempt Organ Donation Event Insert"):
                        try:
                            cursor.execute("""
                                INSERT INTO organ_donation_event (Donor_ID, Recipient_ID, Organ_Matched, Date)
                                VALUES (%s, %s, %s, CURDATE())
                            """, (donor_id, recipient_id, match['required_organ']))
                            conn.commit()
                            st.success("✅ Event inserted — Trigger allowed (pair compatible).")
                        except Exception as e:
                            st.error(f"🚫 Trigger prevented insert: {e}")

                # st.info("💡 Note: trg_check_compatibility_score auto-adjusts Match_Status if score is updated.")
                st.success("🎉 Procedure + Function + Trigger execution completed.")
                st.session_state.comp_step = "select"

            # -----------------------------------------------------------
            # Step 5️⃣: Cleanup
            # -----------------------------------------------------------
            cursor.close()
            conn.close()



    # ---------- EVENTS ----------
    elif menu == "Events":
        st.header("📅 Donation Events")
        conn = get_connection()
        if not conn:
            st.stop()
        cursor = conn.cursor(dictionary=True)
        etype = st.radio("Select Event Type", ["Blood Donation Event", "Organ Donation Event"])

        if etype == "Blood Donation Event":
            # Show existing blood donation events
            cursor.execute("""
    SELECT 
        bde.Event_ID,
        CONCAT(d.First_Name, ' ', d.Last_Name) AS Donor_Name,
        d.Blood_Group AS Donor_BloodGroup,
        CONCAT(r.First_Name, ' ', r.Last_Name) AS Recipient_Name,
        r.Blood_Group AS Recipient_BloodGroup,
        bde.Units_Donated,
        bde.Date,
        bde.Time,
        bde.Location
    FROM Blood_Donation_Event bde
    JOIN Donor d ON bde.Donor_ID = d.Donor_ID
    LEFT JOIN Recipient r ON bde.Recipient_ID = r.Recipient_ID
    ORDER BY bde.Event_ID DESC;
""")

            events = cursor.fetchall()
            
            st.subheader("Record New Blood Donation Event")
            with st.form("blood_donation_form"):
                donor_id = st.number_input("Donor ID", min_value=1, step=1)
                recipient_id = st.number_input("Recipient ID (Optional)", min_value=0)
                if recipient_id == 0:
                    recipient_id = None
                units_donated = st.number_input("Units Donated", min_value=1, step=1)
                date = st.date_input("Date")
                time = st.time_input("Time")
                location = st.text_input("Location")
                submitted = st.form_submit_button("Add Blood Donation Event")
                if submitted:
                    try:
                        insert_query = """
                            INSERT INTO Blood_Donation_Event (Donor_ID, Recipient_ID, Units_Donated, Date, Time, Location)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (donor_id, recipient_id, units_donated, date, time, location))
                        conn.commit()
                        st.success("Blood Donation Event recorded successfully!")
                    except Exception as e:
                        st.error(f"Error recording event: {e}")

        else:
            # Show existing organ donation events
            cursor.execute("SELECT * FROM Organ_Donation_Event")
            events = cursor.fetchall()
            
            st.subheader("Record New Organ Donation Event")
            with st.form("organ_donation_form"):
                donor_id = st.number_input("Donor ID", min_value=1, step=1)
                recipient_id = st.number_input("Recipient ID", min_value=1, step=1)
                organ_matched = st.text_input("Organ Matched")
                doctor_assigned = st.text_input("Doctor Assigned")
                date = st.date_input("Date")
                time = st.time_input("Time")
                location = st.text_input("Location")
                submitted = st.form_submit_button("Add Organ Donation Event")
                if submitted:
                    try:
                        insert_query = """
                            INSERT INTO Organ_Donation_Event (Donor_ID, Recipient_ID, Organ_Matched, Doctor_Assigned, Date, Time, Location)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (donor_id, recipient_id, organ_matched, doctor_assigned, date, time, location))
                        conn.commit()
                        st.success("Organ Donation Event recorded successfully!")
                    except Exception as e:
                        st.error(f"Error recording event: {e}")

        # Display events table with styling
        if events:
            df = pd.DataFrame(events)
            if 'Recipient_ID' in df.columns:
                df['Recipient_ID'] = df['Recipient_ID'].astype('Int64')
            st.table(
                df.style.set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#aa3a2a'), ('color', '#ffcaca')]}
                ]).set_properties(**{
                    'background-color': "#ffecec53",
                    'color': '#2c2c2c',
                    'font-family': 'arial'
                })
            )
        else:
            st.info("No events recorded yet.")
        
        cursor.close()
        conn.close()

