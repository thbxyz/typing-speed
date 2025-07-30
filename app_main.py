import streamlit as st
import random
import datetime
import streamlit.components.v1 as components #this is for the auto scroll to results

st.markdown("## Test your typing speed")

text_bank = ["Wombats poop in cubes. This odd shape helps it to stay in place and mark areas without it rolling off. The shape forms slowly inside their gut as muscles compresses waste in waves. Wombats use the poop to send signals to others about food, space, or danger.",
             "Sloths move very slow and grow green algae on their fur. This helps them hide in trees from danger. They sleep most of the day and poop just once a week. Sloths are also strong swimmers. They use their long arms to move easily through rivers.",
             "Pinapples take a long time to grow. From planting to harvest, it can take over two years for just one fruit. They grow from the ground, not trees. Each plant makes one pineapple at a time. After the initial fruit, it may grow a second, but typically smaller. Second harvests are known as ratoons.",
             "Most clothes are made from blends of fibers. Cotton is soft and breathes well, while nylon or spandex adds stretch. Tags will show what each item is made of. Some shirts can block UV light or dry faster. Others are made to resist stains or stay wrinkle free all day."]

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

if st.session_state["start_status"] == False:
    if st.button("Start Test", type="primary") == True:
        st.session_state["start_status"] = True
        st.session_state["start_time"] = datetime.datetime.now()
        st.session_state["type_text"] = str(random.choice(text_bank))
        st.rerun()

if st.session_state["start_status"] == True:
    text_to_type = st.session_state["type_text"]
    st.markdown("**⏱️Start typing! Take note of the punctuations.**")
    with st.form("typing speed test"):
        st.write("<b>Type this:</b>", unsafe_allow_html=True)
        st.write(text_to_type)
        user_input = st.text_area("Text", placeholder="Type here...", label_visibility="collapsed", disabled=st.session_state["form_disabled"])
        user_submit = st.form_submit_button("submit",disabled=st.session_state["form_disabled"])
    if user_submit == True:
        st.session_state["form_disabled"] = True
        st.session_state["end_time"] = datetime.datetime.now()
        st.rerun()
    if st.session_state["end_time"] != None:
        #st.write(user_submit)#user_submit is False
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
        #Results display
        st.markdown('<div id="results"></div>', unsafe_allow_html=True)#the anchor point for auto scroll, the scrolling script will search for this id="results"
        st.write(f"You typed {len(user_word_list)} words in {time_taken.total_seconds():.2f} seconds.")# :.Xf displays numbers as X number of decimal places
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
                            <p style="font-size: 14px; font-weight: bold; margin-bottom: 1px;">Speed:</p>
                            <p style="font-size: 36px; font-weight: bold; margin-top: 0px; margin-bottom: 1px;">{:.2f}</p>
                            <p style="font-size: 14px; font-weight: bold; margin-top: 0px;">Words Per Minute</p>
                            </div>
                            """.format(user_WPM), unsafe_allow_html=True)               
            with result_display[1]:
                st.markdown("""
                            <div style="text-align:center;">
                            <p style="font-size: 60px; font-weight: bold; margin-top: 3px; margin-bottom: 3px;">×</p>
                            </div>
                            """, unsafe_allow_html=True)
            with result_display[2]:
                st.markdown(f"""
                            <div style="text-align:center;">
                            <p style="font-size: 14px; font-weight: bold; margin-bottom: 1px;">Accuracy:</p>
                            <p style="font-size: 36px; font-weight: bold; margin-top: 0px; margin-bottom: 1px;">{user_accuracy:.0%}</p>
                            <p style="font-size: 14px; font-weight: bold; margin-top: 0px;">{word_error_count} typo(s)</p>
                            </div>
                            """,unsafe_allow_html=True)# :.X% to display as percentage with X number of decimal places
            with result_display[3]:
                st.markdown("""
                            <div style="text-align:center;">
                            <p style="font-size: 60px; font-weight: bold; margin-top: 3px; margin-bottom: 3px;">=</p>
                            </div>
                            """, unsafe_allow_html=True)
            with result_display[4]:
                st.markdown(f"""
                            <div style="text-align:center;">
                            <p style="font-size: 14px; font-weight: bold; margin-bottom: 1px;">Net WPM:</p>
                            <p style="font-size: 36px; font-weight: bold; margin-top: 0px; margin-bottom: 1px;">{(user_WPM * user_accuracy):.2f}</p>
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
    
    if st.button("Retry", type="primary") == True:
        st.session_state["start_time"] = None
        st.session_state["end_time"] = None
        st.session_state["start_status"] = False
        st.session_state["form_disabled"] = False
        st.session_state["type_text"] = random.choices(text_bank)
        st.rerun()


with st.expander("💡How is your typing speed measured?"):
    st.write("""
             Typing speed is determined by a combination of both speed and accuracy, and not just how quickly one can type. 
             Speed is measured in Words Per Minute (WPM), which includes punctuation.
             Accuracy, expressed as a percentage, reflects how many words or characters are typed correctly.
""")
    st.write("Speed (WPM) × Accuracy (%) = Net WPM")







