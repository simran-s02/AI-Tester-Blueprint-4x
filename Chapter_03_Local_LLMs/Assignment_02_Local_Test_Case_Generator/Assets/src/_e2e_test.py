from streamlit.testing.v1 import AppTest

at = AppTest.from_file("app.py", default_timeout=180)
at.run()
at.chat_input[0].set_value("create test cases for JIRA-101").run()
print("marks:")
for m in at.markdown:
    print(" -", repr(m.value[:100]))
print("exceptions:", at.exception)
print("done")
