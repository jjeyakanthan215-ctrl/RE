import sys
from resume_processor import process_resume

try:
    # create a dummy pdf
    with open('dummy.txt', 'w') as f:
        f.write('This is a dummy resume with python and java experience of 5 years.')
    
    res = process_resume('dummy.txt', 'Looking for python dev')
    print('SUCCESS:', res)
except Exception as e:
    print('EXCEPTION:', e)
    import traceback
    traceback.print_exc()
