import streamlit as st
import urllib.parse
import requests
import xml.etree.ElementTree as ET
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import Credentials

# --- IBM WATSONX SETUP ---
# Yahan apni API Key aur Project ID daalein
API_KEY = ""
PROJECT_ID = "id "
URL = ""
# --- LANGFLOW SETUP ---
LANGFLOW_URL = "http"
LANGFLOW_FLOW_ID = "id" # (e.g. 36febfab-a1a8-...)
LANGFLOW_API_KEY = "api key" # (e.g. sk-...)

def get_langflow_summary(text):
    url = f"{LANGFLOW_URL}/api/v1/run/{LANGFLOW_FLOW_ID}"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": LANGFLOW_API_KEY
    }
    payload = {
        "input_value": text,
        "output_type": "chat",
        "input_type": "chat"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['outputs'][0]['outputs'][0]['results']['message']['text']
    except Exception as e:
        return f"Langflow API Error: {e}"



































st.set_page_config(page_title="IBM Research Agent", page_icon="🤖")

st.title("🤖 IBM AI Research Agent")
st.write("Powered by IBM Granite & arXiv")

topic = st.text_input("Research Topic daalein:", "agentic ai in healthcare")

if st.button("Search & Summarize"):
    if topic:
        with st.spinner("arXiv se papers dhoondh rahe hain..."):
            # arXiv API Call
            query = urllib.parse.quote(f'all:"{topic}"')
            url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=2"
            
            try:
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                root = ET.fromstring(response.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                papers = root.findall('atom:entry', ns)
                
                if not papers:
                    st.warning("Is topic par koi paper nahi mila. Kripya topic change karein.")
                else:
                    for paper in papers:
                        title = paper.find('atom:title', ns).text.strip().replace('\n', ' ')
                        abstract = paper.find('atom:summary', ns).text.strip().replace('\n', ' ')
                        link = paper.find('atom:id', ns).text.strip()
                        
                        st.subheader(title)
                        st.write(f"**Link:** {link}")
                        
                        # IBM Granite Setup
                        with st.spinner("IBM Granite summarize kar raha hai..."):
                            try:
                                model = ModelInference(
                                    model_id="ibm/granite-4-h-small",
                                    credentials=Credentials(url=URL, api_key=API_KEY),
                                    project_id=PROJECT_ID,
                                    params={"max_tokens": 300, "temperature": 0.5}
                                )
                                prompt = f"Summarize this research abstract in 3 bullet points and suggest a future hypothesis:\n\nAbstract: {abstract}"
                                reply = model.chat(messages=[{"role": "user", "content": prompt}])
                                summary = reply["choices"][0]["message"]["content"]
                                
                                st.info(summary)
                            except Exception as e:
                                st.error(f"IBM API Error: {e}")
                                
                        st.markdown("---")
            except Exception as e:
                st.error(f"Error fetching papers: {e}")