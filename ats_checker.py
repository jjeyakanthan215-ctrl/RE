import os
import re
from resume_processor import (
    extract_text, 
    preprocess_text, 
    TECH_SKILLS, 
    extract_contact_info, 
    extract_experience,  # noqa: F401
    extract_experience_years,
    extract_education, 
    extract_resume_sections,
    generate_interview_questions
)
def check_ats_score(file_path, job_description):
    # sourcery skip: set-comprehension
    # sourcery skip: set-comprehension
    """
    Advanced ATS Score logic based on 10 modules.
    Returns a comprehensive dict of scores and feedback.
    """
    text = extract_text(file_path)
    filename = os.path.basename(file_path)
    
    if text in ["OCR_FAILED_TESSERACT_NOT_FOUND", "UNSUPPORTED_FORMAT_DOC"] or len(text) < 20:
        return {"error": "Invalid format or unreadable text. Please upload a standard PDF or DOCX."}
        
    lower_text = text.lower()
    lower_jd = job_description.lower()
    resume_words = preprocess_text(text)  # noqa: F841
    jd_words = preprocess_text(job_description)  # noqa: F841
    
    # 1. Keyword Match Score (25%)
    all_candidate_skills = set()
    for skill in TECH_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', lower_text):
            all_candidate_skills.add(skill)
            
    jd_skills = set()
    for skill in TECH_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', lower_jd):
            jd_skills.add(skill)
            
    matched = sorted(list(all_candidate_skills.intersection(jd_skills)))
    missing = sorted(list(jd_skills.difference(all_candidate_skills)))
    
    keyword_score = 0
    if jd_skills:
        keyword_score = (len(matched) / len(jd_skills)) * 25
    else:
        keyword_score = 25 # Default if no skills in JD
        
    # 2. Section Detection & Structure (10%)
    sections = extract_resume_sections(text)
    section_score = 0
    missing_sections = []
    
    required_sections = ["experience", "education", "skills"]
    for req in required_sections:
        if sections.get(req) != "Not Specified":
            section_score += 3.33
        else:
            missing_sections.append(req.capitalize())
            
    # 3. Contact Info (5%)
    email, phone = extract_contact_info(text)
    contact_score = 0
    missing_contact = []
    if email != "Not Found":
        contact_score += 2.5
    else:
        missing_contact.append("Email")
        
    if phone != "Not Found":
        contact_score += 2.5
    else:
        missing_contact.append("Phone Number")
        
    # 4. Experience Relevance & Depth (15%)
    jd_exp_years = extract_experience_years(job_description)
    
    res_exp_text = sections.get("experience", "")
    if res_exp_text == "Not Specified":
        res_exp_years = 0.0
    else:
        # Only check the experience section to avoid counting education years (e.g. 2020-2024)
        res_exp_years = extract_experience_years(res_exp_text)
        
    exp_score = 0
    exp_feedback = ""
    
    if res_exp_years >= jd_exp_years:
        exp_score = 15
        exp_feedback = f"Great! Your experience ({res_exp_years} yrs) meets or exceeds the required ({jd_exp_years} yrs)."
    elif res_exp_years > 0:
        exp_score = 7
        exp_feedback = f"Job requires {jd_exp_years} yrs, but you appear to have {res_exp_years} yrs."
    else:
        exp_score = 0
        exp_feedback = f"Job requires {jd_exp_years} yrs, but no experience was detected on your resume."
        
    # 5. Action Verbs (5%)
    strong_verbs = [
        "developed", "architected", "spearheaded", "optimized", "managed", "led", "created", 
        "designed", "engineered", "built", "deployed", "implemented", "launched", "resolved",
        "transformed", "integrated", "orchestrated", "maximized", "reduced", "increased",
        "generated", "directed", "executed", "innovated", "modernized", "redesigned",
        "streamlined", "upgraded", "accelerated", "achieved", "delivered", "mentored",
        "navigated", "negotiated", "pioneered", "secured", "solved", "structured",
        "supervised", "tested", "validated", "visualized"
    ]
    weak_verbs = ["responsible for", "helped with", "assisted in", "worked on", "duties included"]
    
    strong_count = sum(verb in lower_text for verb in strong_verbs)
    weak_count = sum(verb in lower_text for verb in weak_verbs)
    
    action_verb_score = min(5, (strong_count * 1.5))
    if weak_count > 0:
        action_verb_score -= min(2, weak_count * 0.5)
        action_verb_score = max(0, action_verb_score)
        
    # 6. Education Match (10%)
    jd_edu = extract_education(job_description)
    res_edu = extract_education(text)
    edu_score = 0
    edu_feedback = ""
    
    if jd_edu == "Degree Not Specified":
        edu_score = 10
        edu_feedback = "No specific education required by JD."
    elif res_edu == jd_edu or (
        any(deg in res_edu for deg in ["Master", "PhD", "MCA", "M.Tech", "M.E", "M.Sc"]) and 
        any(deg in jd_edu for deg in ["Bachelor", "Degree Not Specified"])
    ):
        edu_score = 10
        edu_feedback = f"Education exceeds or matches requirements ({res_edu})."
    else:
        edu_score = 5
        edu_feedback = f"Job mentions {jd_edu}, found {res_edu}."
        
    # 7. Length & Readability (5%)
    word_count = len(text.split())
    length_score = 0
    length_feedback = ""
    
    if 200 <= word_count <= 800:
        length_score = 5
        length_feedback = f"Good length ({word_count} words)."
    elif word_count < 200:
        length_score = 2
        length_feedback = f"A bit too short ({word_count} words). Try adding more detail."
    else:
        length_score = 3
        length_feedback = f"A bit too long ({word_count} words). Keep it concise."
        
    # 8. File Format (5%)
    format_score = 5
    format_feedback = "Standard format used."
    if ".doc" in filename.lower():
        format_score = 2
        format_feedback = "Avoid .doc format. Use .pdf or .docx."
        
    # 9 & 10. Bonus & Personalization (20%)
    # Let's group these into a generic relevance score
    relevance_score = 15 if (len(matched) > 0 and exp_score > 5) else 5
    
    total_score = round(keyword_score + section_score + contact_score + exp_score + action_verb_score + edu_score + length_score + format_score + relevance_score)
    total_score = min(100, max(0, total_score))
    
    return {
        "filename": filename,
        "total_score": total_score,
        "breakdown": {
            "keyword_score": round(keyword_score, 1),
            "section_score": round(section_score, 1),
            "contact_score": round(contact_score, 1),
            "exp_score": round(exp_score, 1),
            "action_verb_score": round(action_verb_score, 1),
            "edu_score": round(edu_score, 1),
            "length_score": round(length_score, 1),
            "format_score": round(format_score, 1),
            "relevance_score": round(relevance_score, 1)
        },
        "matched_skills": matched,
        "missing_skills": missing,
        "missing_sections": missing_sections,
        "missing_contact": missing_contact,
        "feedback": {
            "experience": exp_feedback,
            "education": edu_feedback,
            "length": length_feedback,
            "format": format_feedback,
            "action_verbs": f"Found {strong_count} strong verbs and {weak_count} weak phrases."
        },
        "interview_questions": generate_interview_questions(matched, missing, res_exp_years)
    }
