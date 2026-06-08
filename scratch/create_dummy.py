import os

upload_dir = "uploaded_resumes"
os.makedirs(upload_dir, exist_ok=True)
with open(os.path.join(upload_dir, "dummy_resume.txt"), "w") as f:
    f.write("John Doe\nPython, React, SQL\nExperience: 5 years at Google")
