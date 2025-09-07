import streamlit as st
import random
import datetime
import streamlit.components.v1 as components #this is for the auto scroll to results
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

#--------------------
# Database code
#--------------------
load_dotenv()
#load the env variables from the .env file into the process environment, so that the variables in the env file become available to os.getenv()
#load_dotenv() looks for a file named .env in the project root (same folder as the .py file). Once loaded, python sees them as if they were set in the system environment.
#locally, .env is loaded from the machine. But on Render (or other cloud), instead of uploadeing .env file, the env variables are set into Render's environment settings and Render injects them into the runtime environment, so in deployment, the host provides the variable values instead.
#Therefore load_dotenv is actually only needed locally. It is not needed for deployment on Render (or other platforms), where you can just call os.getenv at runtime and it will pickup the value from Render
#But it is ok to just leave the load_dotenv code here, even though it is not needed for Render deployment, it will just not be able to find the .env file (since this file is not pushed to cloud) and do nothing.
#keeping it makes local development more convinient

###db parameters when hosting the db locally on laptop
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = int(os.getenv("DB_PORT", 5432))#need to convert to integer as env var type is string. The port variable should be a integer.
# DB_NAME = os.getenv("DB_NAME", "leaderboard_db")
# DB_USER = os.getenv("DB_USER", "postgres")#postgres is the default super user
# DB_PASSWORD = os.getenv("DB_PASSWORD","")#for password, the default is not set into the default for security reason
# DB_SSLMODE = os.getenv("DB_SSLMODE") or "prefer"
###
###Hosting the db on render.com
RENDER_EXT_DB_URL = os.getenv("RENDER_EXT_DB_URL")
if not RENDER_EXT_DB_URL:
    raise ValueError("Database not found.")
#the render db url packs all the separate db parameters into it, passing this url is equivalent to getting all necessary parameters
#note that the parameter values are not the same as when hosting the db locally

# kwargs = {
#     "host":DB_HOST,
#     "port":DB_PORT,
#     "dbname":DB_NAME,
#     "user":DB_USER,
#     "password":DB_PASSWORD,
#     "sslmode":DB_SSLMODE
# }#dictionary to store the arguments needed for connection to db. kwargs is the common naming convention for this, but not necessary muct use this name.
# def get_connection():
#     return psycopg2.connect(**kwargs)
#     #this connects to the database with your user and password, it is the same as passing arguments this way "host"=DB_HOST
#     # *args(unpacks lists/tuples)
#     # **kwargs(unpacks dictionaries)

def get_connection():
    return psycopg2.connect(RENDER_EXT_DB_URL)

def init_db():
    conn = get_connection()
    c = conn.cursor()#creates a 'cursor' object to send SQL commands in python. 
    #In python, 'cursor' is a the primary interface you use to interact with the database within your Python code.
    #However in a pure SQL world, a 'cursor' is an object for iterating though the selected set row by row. Same name, but two different things.
    #Execute SQL command to create a table named leaderboard if it does not exist, with columns for name, wpm and date
    #TEXT are string values, REAL are a type of float data type for floating point numbers
    c.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
              id SERIAL PRIMARY KEY,
              name TEXT,
              wpm REAL,
              accuracy REAL,
              netwpm REAL,
              date TEXT
              )
              ''')
    conn.commit()#.commit basically means "save changes" to the database. 
    #Any commands like INSERT or UPDATE etc. ran in SQLite, Python will store those changes temporarily 
    #Nothing is written to the .db file, until you run the .commit command.
    #Without running .commit, the changes in python may seem to work while the program is running, once connection is closed/program stops, those changes will vanish.
    c.close()#good practice to close the connection each time after querying, instead of leaving a connection forever open
    conn.close()#good practice to close the connection each time
    #or we can just use the with statement to close the connections automatically without hacing to call .close()

def add_score(name, wpm, accuracy, netwpm):
    with get_connection() as conn:#this way i no need to call conn.close() at the end
        with conn.cursor() as c:#this way i no need to call c.close() at the end
            date_now = datetime.datetime.now().strftime(r"%d/%m/%Y, %H:%M:%S")
            c.execute("INSERT INTO leaderboard (name, wpm, accuracy, netwpm, date) VALUES (%s,%s,%s,%s,%s)",(name, wpm, accuracy, netwpm, date_now))
            #INSERT INTO tabl (col1, col2, col3) VALUES (?, ?, ?) within a Python code, the ? symbols are placeholders for values. 
            #This is a common and important practice when using Python to interact with a database, specifically to prevent SQL injection attacks.
            #cursor.execute(sql_command_with_?_placeholders, data_to_insert_into_placeholders)
            #SQLite uses (?,?,?) as placeholders, postgres uses (%s,%s,%s) as placeholders 
            conn.commit()

def get_leaderboard():
    with get_connection() as conn:
        with conn.cursor() as c:
            c.execute("SELECT name, wpm, accuracy, netwpm, date FROM leaderboard ORDER BY netwpm DESC LIMIT 5")
            leader_rows = c.fetchall()
    return leader_rows
    #After you execute a SELECT query using cursor.execute(), the result set is available on the cursor. 
    #The .fetchall() method retrieves all of these rows at once. 
    #Each row is represented as a tuple, and all of these tuples are collected into a single list.
    #i.e. [(1, 'tuple'),(2, 'tuple2'),(3, 'tuple3')]


#------------------------
# Streamlit code (main)
#------------------------

init_db()
st.markdown("## Test your typing speed")

with open("text_bank.txt","r",encoding="utf-8") as f:
    raw_text = f.read()
    text_bank = [t.strip() for t in raw_text.split("---") if t.strip() != ""] #this syntax is list comprehension, is a way to create lists using a concise syntax
    #after .strip(), it is possible to have empty strings "" that may cause issues, by adding if t.strip() != "" removes such text that will cause problem
    #Read more on list comprehension: https://www.w3schools.com/python/python_lists_comprehension.asp

if "start_time" not in st.session_state:
    st.session_state["start_time"] = None
if "end_time" not in st.session_state:
    st.session_state["end_time"] = None
if "start_status" not in st.session_state:
    st.session_state["start_status"] = False
if "form_disabled" not in st.session_state:
    st.session_state["form_disabled"] = False
if "type_text" not in st.session_state:
    st.session_state["type_text"] = ""
if "save_res" not in st.session_state:
    st.session_state["save_res"] = False
if "res" not in st.session_state:
    st.session_state["res"] = []
if "save_result_button_disable" not in st.session_state:
    st.session_state["save_result_button_disable"] = False

def reset_defaults_and_rerun():
    st.session_state["start_time"] = None
    st.session_state["end_time"] = None
    st.session_state["start_status"] = False
    st.session_state["form_disabled"] = False
    st.session_state["type_text"] = random.choices(text_bank)
    st.session_state["save_res"] = False
    st.session_state["res"] = []
    st.session_state["save_result_button_disable"] = False
    #st.rerun() #streamlit now no longer requires an explicit rerun, it reruns automatically

if st.session_state["start_status"] == False:
    if st.button("Start Test", type="primary") == True:
        st.session_state["start_status"] = True
        st.session_state["start_time"] = datetime.datetime.now()
        st.session_state["type_text"] = str(random.choice(text_bank))
        st.rerun()

if st.session_state["start_status"] == True:
    text_to_type = st.session_state["type_text"]
    st.markdown("**⏱️Start typing! Take note of punctuations and capital letters.**")
    with st.form("typing speed test"):
        st.write("<b>Type this:</b>", unsafe_allow_html=True)
        st.write(text_to_type)
        user_input = st.text_area("Text", placeholder="Type here...", label_visibility="collapsed", disabled=st.session_state["form_disabled"])
        user_submit = st.form_submit_button("submit",disabled=st.session_state["form_disabled"])
    if user_submit == True and user_input.strip()=="":
        st.error("Nothing has been typed, please take the test again.")
    if user_submit == True and user_input.strip()!="":
        st.session_state["form_disabled"] = True
        st.session_state["end_time"] = datetime.datetime.now()
        st.rerun()
    if st.session_state["end_time"] != None:
        time_taken = st.session_state["end_time"] - st.session_state["start_time"]
        user_input_trim = user_input.strip()
        text_word_list = text_to_type.split()
        user_word_list = user_input_trim.split()
        #speed
        user_WPM = len(user_word_list) / (time_taken.total_seconds() / 60)
        #accuracy       
        word_error_count = 0
        user_accuracy = 1
        for i in range(len(user_word_list)):
            if user_word_list[i] != text_word_list[i]:
                word_error_count += 1
        user_accuracy = 1 - (word_error_count / len(user_word_list))
        net_WPM = user_WPM*user_accuracy
        st.session_state["res"] = [f"{user_WPM:.2f}", user_accuracy, f"{net_WPM:.2f}"]
        #Results display
        st.markdown('<div id="results"></div>', unsafe_allow_html=True)#the anchor point for auto scroll, the scrolling script will search for this id="results"
        st.write(f"You typed {len(user_word_list)} words in {time_taken.total_seconds():.2f} seconds.")# :.Xf displays numbers as X number of decimal places
        
        #Adding this code right in front of the results display section
        #to remove the extra spacing after the results container
        #but I have no idea what these html and css means and why by inserting this css code removes the space
        custom_css = """
        <style>
            /* Rule 1: Target the container of st.columns */
            div[data-testid="stHorizontalBlock"] {
                align-items: flex-start;
            }
            /* Rule 2: Target the stElementContainer that holds the iframe */
            /* This is the div that creates the unwanted vertical space */
            div[data-testid="stElementContainer"]:has(iframe[data-testid="stIFrame"]) {
                padding: 0 !important;
                margin: 0 !important;
                height: 0 !important;
                overflow: hidden !important; /* Ensures no content overflows */
            }
        </style>
        """
        # Inject the custom CSS
        st.markdown(custom_css, unsafe_allow_html=True)

        st.markdown("## :red[Your results:]")
        with st.container(border=True):
            result_display = st.columns(5)
            with result_display[0]:   
                #for strings that are too long and will span multiple lines, we can use """......."""
                #.format() works like this
                # formatted = "{:.2f}".format(before_format)
                #or we can also use {user_WPM:.2f} - but for this case remember to use f-string
                st.markdown("""
                            <div style="text-align:center;">
                            <p style="font-size: 14px; font-weight: bold; margin-bottom: 0px;">Speed:</p>
                            <p style="font-size: 36px; font-weight: bold; margin-top: 0px; margin-bottom: 0px;">{:.2f}</p>
                            <p style="font-size: 14px; font-weight: bold; margin-top: 0px;">Words Per Minute</p>
                            </div>
                            """.format(user_WPM), unsafe_allow_html=True)               
            with result_display[1]:
                st.markdown("""
                            <div style="text-align:center;">
                            <p style="font-size: 58px; font-weight: bold; margin-top: 0px; margin-bottom: 0px;">×</p>
                            </div>
                            """, unsafe_allow_html=True)
            with result_display[2]:
                st.markdown(f"""
                            <div style="text-align:center;">
                            <p style="font-size: 14px; font-weight: bold; margin-bottom: 0px;">Accuracy:</p>
                            <p style="font-size: 36px; font-weight: bold; margin-top: 0px; margin-bottom: 0px;">{user_accuracy:.0%}</p>
                            <p style="font-size: 14px; font-weight: bold; margin-top: 0px;">{word_error_count} typo(s)</p>
                            </div>
                            """,unsafe_allow_html=True)# :.X% to display as percentage with X number of decimal places
            with result_display[3]:
                st.markdown("""
                            <div style="text-align:center;">
                            <p style="font-size: 58px; font-weight: bold; margin-top: 0px; margin-bottom: 0px;">=</p>
                            </div>
                            """, unsafe_allow_html=True)
            with result_display[4]:
                st.markdown(f"""
                            <div style="text-align:center;">
                            <p style="font-size: 14px; font-weight: bold; margin-bottom: 0px;">Net WPM:</p>
                            <p style="font-size: 36px; font-weight: bold; margin-top: 0px; margin-bottom: 0px;">{(user_WPM * user_accuracy):.2f}</p>
                            <p style="font-size: 14px; font-weight: bold; margin-top: 0px;">Words Per Minute</p>
                            </div>
                            """,unsafe_allow_html=True)

        #auto scroll to results
        #<script>....</script> tells the browser to excecute the code inside as JavaScript
        components.html("""
                        <script>
                        setTimeout(function(){    
                            const element = window.parent.document.getElementById("results");
                                if(element) {
                                    element.scrollIntoView({behavior:"smooth"});
                                }
                        }, 100);
                        </script>
                        """, height=0)
        #height=0 means this embedded content does not take up visible space, we are only using this for scrolling effects
        #JavaScript const element means declaring a const variable named element
    
        if st.button("Save my results", type="primary", disabled=st.session_state["save_result_button_disable"]):
            st.session_state["save_result_button_disable"] = True
            st.session_state["save_res"] = True
            st.rerun()
        if st.session_state["save_res"] == True:
            username = st.text_input("What is your name?")
            if username != "" and st.session_state["res"] != []:
                add_score(username, st.session_state["res"][0], st.session_state["res"][1], st.session_state["res"][2])
                st.success("Result saved!")
                reset_defaults_and_rerun()
                st.rerun()
    
    st.button("Retry", type="primary", on_click=reset_defaults_and_rerun)           
    
st.markdown("### Leaderboard (Top 5)")
leaderboard_data = get_leaderboard()
leader_names = []
leader_WPM = []
leader_accuracy = []
leader_netWPM = []
leader_timestamp = []
for t in leaderboard_data:
    leader_names.append(t[0])
    leader_WPM.append(f"{t[1]} WPM")
    leader_accuracy.append(f"{t[2]:.0%}")
    leader_netWPM.append(f"{t[3]} WPM")
    leader_timestamp.append(t[4])
leaderboard_table = {"Name":leader_names, "Speed": leader_WPM, "Accuracy":leader_accuracy, "Net WPM":leader_netWPM, "Timestamp":leader_timestamp}
st.dataframe(leaderboard_table)

with st.expander("💡How is my typing speed measured?"):
    st.write("""
             Typing speed is determined by a combination of both speed and accuracy, and not just how quickly one can type. 
             Speed is measured in Words Per Minute (WPM), which includes punctuation.
             Accuracy, expressed as a percentage, reflects how many words or characters are typed correctly.
""")
    st.write("Speed (WPM) × Accuracy (%) = Net WPM")


