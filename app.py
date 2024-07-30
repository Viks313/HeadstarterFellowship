from flask import Flask, render_template, request
import pdfplumber
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

def calculate_ats_score(resume_text, job_description_text):
    texts = [resume_text, job_description_text]
    count_vectorizer = CountVectorizer().fit_transform(texts)
    vectors = count_vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    score = cosine_sim[0][1]
    return score * 100

def extract_skills_and_experience(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    skills = []
    experience = []
    custom_skills = [
        "Python", "Java", "SQL", "JavaScript", "C++", "Project Management", "Machine Learning", 
        "Data Analysis", "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management",
        "Adaptability", "Creativity", "Work Ethic", "Attention to Detail", "Interpersonal Skills",
        "Customer Service", "Sales", "Marketing", "Financial Analysis", "Accounting", "Budgeting",
        "Programming", "Web Development", "Software Engineering", "Database Management", "Networking",
        "Cloud Computing", "Artificial Intelligence", "Research", "Data Mining", "Big Data", "Data Visualization"
    ]

    for token in doc:
        if token.text in custom_skills:
            skills.append(token.text)
        if token.ent_type_ in {"ORG", "WORK_OF_ART", "PRODUCT"}:
            experience.append(token.text)
    
    return list(set(skills)), list(set(experience))

def extract_required_skills(job_description_text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(job_description_text)
    
    custom_skills = [
        "Python", "Java", "SQL", "JavaScript", "C++", "Project Management", "Machine Learning", 
        "Data Analysis", "Communication", "Leadership", "Teamwork", "Problem Solving", "Time Management",
        "Adaptability", "Creativity", "Work Ethic", "Attention to Detail", "Interpersonal Skills",
        "Customer Service", "Sales", "Marketing", "Financial Analysis", "Accounting", "Budgeting",
        "Programming", "Web Development", "Software Engineering", "Database Management", "Networking",
        "Cloud Computing", "Artificial Intelligence", "Research", "Data Mining", "Big Data", "Data Visualization"
    ]

    required_skills = [token.text for token in doc if token.text in custom_skills]
    
    return list(set(required_skills))

def generate_suggestions(skills, experience, job_description_text):
    suggestions = []
    
    if not skills:
        suggestions.append("Consider adding more relevant skills to your resume that align with the job description.")
    else:
        suggestions.append("Skills matched with job description: " + ", ".join(skills))
    
    if not experience:
        suggestions.append("Consider adding more detailed descriptions of your work experience, including specific projects and achievements.")
    else:
        suggestions.append("Experience listed in resume: " + ", ".join(experience))
    
    if len(skills) < 3:
        suggestions.append("Add more specific skills that match the job description.")
    
    if len(experience) < 2:
        suggestions.append("Provide more details about your work experience, including specific projects and achievements.")

    if len(skills) < 3 or len(experience) < 2:
        suggestions.append("Review the job description and ensure your resume highlights the skills and experiences that are most relevant to the position.")

    return suggestions

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return "No file part"
    if 'job_description' not in request.form:
        return "No job description part"
    
    file = request.files['resume']
    job_description = request.form['job_description']
    
    if file.filename == '':
        return "No selected file"
    if file and file.filename.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()

            ats_score = calculate_ats_score(text, job_description)
            skills, experience = extract_skills_and_experience(text)
            required_skills = extract_required_skills(job_description)
            skills_review = f"Identified Skills ({len(skills)}): {', '.join(skills)}"
            experience_review = f"Identified Experience ({len(experience)}): {', '.join(experience)}"
            suggestions = "\n".join(generate_suggestions(skills, experience, job_description))

            return render_template('result.html', 
                                   ats_score=f"ATS Score: {ats_score:.2f}", 
                                   skills_review=skills_review, 
                                   experience_review=experience_review, 
                                   suggestions=suggestions,
                                   present_skills=skills,
                                   required_skills=required_skills)
    return "Invalid file type"

if __name__ == "__main__":
    app.run(debug=True)
