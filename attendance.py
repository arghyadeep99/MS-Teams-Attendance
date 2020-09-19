import base64
import datetime
from datetime import datetime
import pandas as pd
import streamlit as st
from PIL import Image
import io

st.title('MS-Teams Attendance Formatter')
st.markdown('Convert your MS Teams attendance CSV into easy-to-read format!')
logo = Image.open("./logo.jpg")
st.sidebar.title("MS-Teams Attendance Formatter")

st.set_option('deprecation.showfileUploaderEncoding', False)

st.sidebar.image(logo, use_column_width=True)
st.sidebar.markdown("This app analyzes your WhatsApp Chats")

st.sidebar.markdown('[![Arghyadeep Das]\
					(https://img.shields.io/badge/Author-@arghyadeep99-gray.svg?colorA=gray&colorB=dodgerblue&logo=github)]\
					(https://github.com/arghyadeep99)')

st.sidebar.markdown('**How to export the attendance in .csv format?**')
st.sidebar.markdown('1) Download the attendance by clicking on the arrow.')
step1 = Image.open("./step1.jpg")

st.sidebar.image(step1, use_column_width=True)

st.sidebar.markdown('2) Open the CSV and it should look something like this:')
step2 = Image.open(r"./step2.jpg")

st.sidebar.image(step2, use_column_width=True)

st.sidebar.markdown('3) Upload this CSV file to this website.')
st.sidebar.markdown('4) Download the resultant CSV that is easier to interpret.')

st.sidebar.markdown('*You are all set to go!* 😃')
st.sidebar.subheader('**FAQs**')
st.sidebar.markdown('**Is the attendance sheet saved on your servers?**')
st.sidebar.markdown('No, the data that you upload is not saved anywhere on this website or any 3rd party website i.e, not in any storage like database/File System/Logs/Cloud.')

uploaded_file = st.file_uploader("Upload Your Attendance Sheet (.csv file only!)", type="csv")

if uploaded_file is not None:
	@st.cache(allow_output_mutation=True)
	def calculate_attendance(file, start_time=None, end_time=None, encoding='utf-8', separator=','):
		file = pd.read_csv(file, encoding=encoding, sep=separator)
		file.Timestamp = pd.to_datetime(file['Timestamp'], infer_datetime_format=True)
		
		df = pd.DataFrame(columns = ["Full Name", "Total Time"])
		df["Full Name"] = file["Full Name"]
		names = df["Full Name"].unique().tolist()
			
		try:
			for i in df.index:
				stud_join_time, stud_left_time = start_time, end_time
				time_attended = end_time - end_time
				join_flag, leave_flag = False, False
				for j in file.index:
					if df['Full Name'][j] == file['Full Name'][i]:
						if file['User Action'][j] == 'Joined before':
							first_join_time = start_time
							stud_join_time = start_time
							time_attended = end_time - stud_join_time
						elif file['User Action'][j] == 'Left':
							stud_left_time = file['Timestamp'][j]
							time_attended -= (end_time - stud_left_time)
						elif file['User Action'][j] == 'Joined':
							stud_join_time = file['Timestamp'][j]

							time_attended += (end_time - stud_join_time)
				df["Total Time"][i] = time_attended

			df['Total Time'] = pd.to_timedelta(df['Total Time'])
			df['Total Time'] = df['Total Time'] - pd.to_timedelta(df['Total Time'].dt.days, unit='d')
			df = df.drop_duplicates()

		except Exception as e:
			print(e)

		df = df.dropna()
		df.reset_index(drop=True)
		df.index = range(1,len(df)+1)
		return df

	encoding = st.selectbox('Enter Encoding option:', ['utf-8', 'utf-7', 'utf-16', 'ISO-8859-1'])
	sep = st.selectbox('Separator:', [',', '\\t', '\\s', ';'])

	start_date = st.date_input("Enter Meeting Date(YYYY/MM/DD):",value=datetime.now())
	st.write("Start date:", start_date)
	
	start_time = st.time_input("Enter Meeting Start Time(HH:MM):",value=datetime.now().time())
	end_time = st.time_input("Enter Meeting End Time(HH:MM):",value=datetime.now().time())

	start_time = datetime.combine(start_date, start_time)
	end_time = datetime.combine(start_date, end_time)

	if st.button("SUBMIT"):	
		df = calculate_attendance(uploaded_file, start_time, end_time, encoding, sep)
		csv = df.to_csv(index=False)
		b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
		href = f'<a href="data:file/csv; base64,{b64}">Download CSV File</a>'

		st.markdown("When clicking on the link below, make sure to save it as <filename>.csv. Don't forget to add the csv extension.")
		st.markdown(href, unsafe_allow_html=True)

		st.table(df)
	else:
		start_time = start_time
		end_time = end_time

