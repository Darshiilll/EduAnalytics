EduAnalytics Authentication Update

CONTENTS
- app.py, database.py, data_utils.py, auth.py
- Updated copies of all eight existing pages in pages/
- New pages/0_Teacher_Accounts.py (Admin-only)

INSTALL
1. Stop Streamlit.
2. BACK UP your existing data/eduanalytics.db file before replacing code.
3. Extract this ZIP into your existing EduAnalytics project folder.
   Keep the folder structure and allow the included files to replace the
   matching source files. Do not delete your other project files.
4. Keep your existing assets/, data/, models/, recommendation_engine.py,
   risk_engine.py, report_generator.py, and requirements.txt files.
5. Start the app as usual: streamlit run app.py

FIRST RUN
- If the database has no Admin account, the app displays a one-time Admin
  setup form. Create the Admin account there.
- After that, the normal login screen appears.
- Log in as Admin. Use the new Teacher Accounts page in the sidebar to
  create individual teacher accounts.
- Teachers log in with the email and password provided by the Admin.

SECURITY / DATA NOTES
- Passwords are stored as PBKDF2-HMAC-SHA256 hashes, not plain text.
- Teacher registration is not public; only an authenticated Admin can
  create teacher accounts.
- Admin can disable and re-enable teacher accounts.
- Each teacher has separate credentials, but all teachers currently work
  with the same existing EduAnalytics student and examination database.
- Authentication is held in the Streamlit session. Logging out clears it.
- This update adds no third-party Python package requirement.
