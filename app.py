import streamlit as st
import os
from pypdf import PdfReader
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

# --- Load Environment Variables ---
# This should be at the top to ensure variables are loaded before they are needed.
load_dotenv()
#Wassup buds
# --- Helper Function to Extract Text from PDFs ---
def get_pdf_text(pdf_docs):
    """
    Extracts text from a list of uploaded PDF files.
    """
    text_dict = {}
    for pdf in pdf_docs:
        try:
            pdf_reader = PdfReader(pdf)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            text_dict[pdf.name] = text
        except Exception as e:
            st.error(f"Error reading {pdf.name}: {e}")
            text_dict[pdf.name] = None
    return text_dict

# --- Streamlit UI Configuration ---
st.set_page_config(page_title="GenAI Resume Ranker", layout="wide", page_icon="🤖")

# --- Load Azure Credentials from .env file ---
# These are loaded once at the start.
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
azure_openai_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# --- Main Application Interface ---
st.title("🤖 AI-Powered Resume Ranker")
st.markdown("""
Welcome to the AI Resume Ranker! This tool helps you quickly evaluate resumes against a job description.
**How it works:**
1.  Ensure your Azure credentials are set in the `.env` file.
2.  Paste the job description into the text area below.
3.  Upload up to 10 resumes in PDF format.
4.  Click the 'Rank Resumes' button to get a scored and ranked list.
""")

# --- Input Fields for JD and Resumes ---
st.header("1. Enter the Job Description")
job_description = st.text_area("Paste the Job Description here...", height=200, key="jd")

st.header("2. Upload Resumes (Max 10)")
uploaded_files = st.file_uploader(
    "Choose PDF files...", 
    type="pdf", 
    accept_multiple_files=True,
    key="resumes"
)
if uploaded_files and len(uploaded_files) > 10:
    st.warning("You can only upload a maximum of 10 resume files. Please remove some files.")
    uploaded_files = uploaded_files[:10]

# --- Submission Button ---
submit_button = st.button("Rank Resumes", type="primary")

# --- Core Logic on Button Click ---
if submit_button:
    # 1. Validate Inputs
    if not all([azure_openai_endpoint, azure_openai_api_key, azure_openai_api_version, azure_openai_deployment_name]):
        st.error("Azure credentials are not configured. Please check your .env file.")
    elif not job_description:
        st.warning("Please enter a Job Description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        with st.spinner("Processing... This may take a few moments depending on the number of resumes."):
            try:
                # 2. Extract text from PDFs
                resume_texts = get_pdf_text(uploaded_files)

                # 3. Define the LangChain model, parser, and prompt
                # LangChain's AzureChatOpenAI will automatically use the environment variables
                # if they are named correctly (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT).
                llm = AzureChatOpenAI(
                    azure_deployment=azure_openai_deployment_name,
                    api_version=azure_openai_api_version,
                    temperature=0.1
                )
                
                prompt_template_string = """
                You are a highly skilled HR professional with expertise in evaluating resumes against job descriptions in the tech industry. 
                Your task is to analyze the provided resume and job description and return a structured JSON response.

                **Job Description:**
                ```
                {jd}
                ```

                **Resume Text:**
                ```
                {resume_text}
                ```

                Please provide the following in a single, valid JSON object and nothing else. Do not include any explanatory text before or after the JSON.
                1. "score": An integer percentage from 0 to 100 representing how well the resume matches the job description. 100 is a perfect match.
                2. "strengths": A brief, single-string summary of the candidate's key strengths that align with the job description. Use bullet points (e.g., "- Strength 1\\n- Strength 2").
                3. "weaknesses": A brief, single-string summary of areas where the resume is weak or missing key requirements. Use bullet points (e.g., "- Weakness 1\\n- Weakness 2").
                4. "summary": A one-sentence summary of the overall fit.

                **JSON Output:**
                """
                
                parser = JsonOutputParser()
                prompt = PromptTemplate(
                    template=prompt_template_string,
                    input_variables=["jd", "resume_text"],
                    partial_variables={"format_instructions": parser.get_format_instructions()}
                )
                
                chain = prompt | llm | parser

                # 4. Process each resume
                results = []
                for filename, resume_text in resume_texts.items():
                    if resume_text:
                        try:
                            response = chain.invoke({"jd": job_description, "resume_text": resume_text})
                            response['filename'] = filename
                            results.append(response)
                        except OutputParserException as ope:
                            st.error(f"Failed to parse LLM output for {filename}. Skipping. Error: {ope}")
                        except Exception as e:
                            st.error(f"An error occurred while processing {filename}: {e}")
                
                # 5. Sort and Display Results
                if results:
                    st.success("Analysis Complete!")
                    st.header("Ranked Resume Results")
                    
                    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
                    
                    for i, result in enumerate(sorted_results):
                        score = result.get('score', 'N/A')
                        with st.expander(f"**{i+1}. {result['filename']}  |  Score: {score}%**", expanded=i==0):
                            st.subheader("Summary")
                            st.write(result.get('summary', 'Not available.'))
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("✅ Strengths")
                                st.markdown(result.get('strengths', 'Not available.').replace('\n', '\n\n'))
                                
                            with col2:
                                st.subheader("❌ Weaknesses")
                                st.markdown(result.get('weaknesses', 'Not available.').replace('\n', '\n\n'))
                else:
                    st.warning("Could not process any of the uploaded resumes. Please check the files and try again.")

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.info("Please check your Azure credential configuration and network connection.")