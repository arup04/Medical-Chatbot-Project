import sys
import os
import io

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.chat_history import add_message, get_chat_history, clear_session_history, get_all_sessions
from langchain_core.messages import HumanMessage, AIMessage


def run_tests():
    all_passed = True
    test_db = os.path.join(os.path.dirname(__file__), "test_chat_history.db")

    # Clean up prior test db if exists
    if os.path.exists(test_db):
        os.remove(test_db)

    print("==================================================================")
    print("            RUNNING SQLITE CHAT HISTORY UNIT TESTS                ")
    print("==================================================================\n")

    session_id = "test_clinical_session_001"

    # 1. Test Inserting Messages
    add_message(session_id, "human", "What is Metformin?", db_path=test_db)
    add_message(session_id, "ai", "Metformin is an oral antidiabetic medication.", db_path=test_db)
    add_message(session_id, "human", "What are its common side effects?", db_path=test_db)
    add_message(session_id, "ai", "Common side effects include nausea and diarrhea.", db_path=test_db)

    # 2. Test Fetching Full History
    history = get_chat_history(session_id, limit=6, db_path=test_db)
    passed1 = len(history) == 4
    passed2 = isinstance(history[0], HumanMessage) and (history[0].content == "What is Metformin?")
    passed3 = isinstance(history[1], AIMessage)
    passed4 = isinstance(history[2], HumanMessage) and (history[2].content == "What are its common side effects?")
    
    print(f"Test #01 {'[PASS]' if passed1 else '[FAIL]'} Total message count = 4: {passed1}")
    print(f"Test #02 {'[PASS]' if passed2 else '[FAIL]'} Turn 1 HumanMessage content verified: {passed2}")
    print(f"Test #03 {'[PASS]' if passed3 else '[FAIL]'} Turn 1 AIMessage type verified: {passed3}")
    print(f"Test #04 {'[PASS]' if passed4 else '[FAIL]'} Turn 2 HumanMessage follow-up verified: {passed4}")

    if not (passed1 and passed2 and passed3 and passed4):
        all_passed = False

    # 3. Test Sliding Window Limit (e.g. limit = 2)
    recent_history = get_chat_history(session_id, limit=2, db_path=test_db)
    passed5 = len(recent_history) == 2 and recent_history[0].content == "What are its common side effects?"
    print(f"Test #05 {'[PASS]' if passed5 else '[FAIL]'} Sliding window (limit=2) returns last 2 turns: {passed5}")
    if not passed5:
        all_passed = False

    # 4. Test Listing Sessions
    sessions = get_all_sessions(db_path=test_db)
    passed6 = session_id in sessions
    print(f"Test #06 {'[PASS]' if passed6 else '[FAIL]'} Session listed in get_all_sessions: {passed6}")
    if not passed6:
        all_passed = False

    # 5. Test Clear History
    clear_session_history(session_id, db_path=test_db)
    cleared_history = get_chat_history(session_id, limit=6, db_path=test_db)
    passed7 = len(cleared_history) == 0
    print(f"Test #07 {'[PASS]' if passed7 else '[FAIL]'} History cleared successfully: {passed7}")
    if not passed7:
        all_passed = False

    # Clean up test db file
    if os.path.exists(test_db):
        os.remove(test_db)

    print("\n" + "=" * 66)
    if all_passed:
        print("ALL SQLITE CHAT HISTORY TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME CHAT HISTORY TESTS FAILED.")
    print("=" * 66)
    return all_passed


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    success = run_tests()
    sys.exit(0 if success else 1)
