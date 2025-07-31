from flask import Flask, render_template, request # Added render_template
import google.generativeai as genai
import os
import PyPDF2




# app
app = Flask(__name__)


#set up the google api key 
os.environ["GOOGLE_API_KEY"]="AIzaSyCRQTEwo9BKFVcgyx9HvR_oCD0znMKuSdc"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

#Initialize the Gemini model
model= genai.GenerativeModel("gemini-1.5-flash")

#function 
# functions
def predict_fake_or_real_email_content(text):
    prompt = f""""
    You are an expert in identifying scam messages in text, email etc. Analyze the given text:

        - **Real/Legitimate** (Authentic, safe message)
        - **Scam/Fake** (Phishing, fraud, or suspicious message)

        **for the following Text:**
        {text}

        **Return a clear message indicating whether this content is real or a scam.  
        If it is a scam, mention why it seems fraudulent. If it is real, state that it is leg  

        **Only return the classification message and nothing else.**  
        Note: Don't return empty or null, you only need to return message for the input text ...  
        """
    response = model.generate_content(prompt)
    return response.text.strip()

def URL_detection(url):
    prompt = f"""
You are an advanced AI model specializing in URL security classification. Analyze the given URL and classify it:

1. **Benign**: Safe, trusted, and non-malicious websites such as google.com, wikipedia.org, amazon.com.
2. **Phishing**: Fraudulent websites designed to steal personal information. Indicators include misspelled domains
3. **Malware**: URLs that distribute viruses, ransomware, or malicious software. Often includes automatic download
4. **Defacement**: Hacked or defaced websites that display unauthorized content, usually altered by attackers.

**Example URLs and Classifications:**
- **Benign**: "https://www.microsoft.com/"
- **Phishing**: "http://secure-login.paypal.com/"
- **Malware**: "http://free-download-software.xyz/"
- **Defacement**: "http://hacked-website.com/"

#Input URL: {url}

**Output Format:**  
- Return only a string class name  
- Example output for a phishing site: "phishing"

Analyze the URL and return the correct classification (Only name in lowercase such as benign etc.).
Note: Don't return empty or null, at any cost return the corrected class.
"""
    response = model.generate_content(prompt)
    return response.text if response else "detection failed"

# routes
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/scam/" , methods= ['GET','POST'])
def detect_scam():
    if "file" not in request.files:
        return render_template("index.html" , message="No file uploaded")
    file = request.files['file']



    extracted_text=""
    if file.filename.endswith(".pdf"):
        pdf_reader=PyPDF2.PdfReader(file)
        extracted_text= " ".join([page.extract_text() for page in pdf_reader.pages  if page.extract_text()])
    elif file.filename.endswith(".txt"):
        extracted_text= file.read().decode("utf-8")
    else:
        return render_template('index.html', message='file is empty or could not extracted text ')
    
    message = predict_fake_or_real_email_content((extracted_text))
    
    return render_template('index.html', message=message)



@app.route("/predict",  methods=["GET","POST"])
def url_predict():
        url = request.form.get("url", '').strip()
        if not url.startswith(('http://','https://')):
            return render_template("index.html", message="Invalid URL format......")
        
        classification = URL_detection(url)
        return render_template('index.html', input_url=url, predicted_class=classification)

# python main
if __name__ == "__main__":
    app.run(debug=True)

