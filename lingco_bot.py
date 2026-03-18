import requests
import json
import time
import random
import sys



def main():

    VOCAB_SET_ID = input("What is the VOCAB_SET_ID? ").strip()
    JWT         = input("What is your JWT token? ").strip()
    SESSION_ID  = input("What is your session ID (number in URL)? ").strip()
    SESSION_UUID = input("What is your session UUID (from X-User-Session-UUID header)? ").strip()

    print(f"\nStarting automated posting for VOCAB_SET_ID: {VOCAB_SET_ID}\n")

    headers = {
        "Authorization": f"Bearer {JWT}",
        "X-User-Session-UUID": SESSION_UUID,
        "Content-Type": "application/json",
    }

    # Fetch vocab set
    url = f"https://class.lingco.io/api/content/vocab_sets/{VOCAB_SET_ID}?progress=true"
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        print(f"Error: vocab set request failed with HTTP {resp.status_code}")
        print(resp.text)
        input("\nPress Enter to exit...")
        sys.exit(1)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        print("Error: invalid JSON response from API")
        print(resp.text)
        input("\nPress Enter to exit...")
        sys.exit(1)

    terms = data.get("terms", [])
    if not terms:
        print("Error: No terms found in this vocab set. Check VOCAB_SET_ID, JWT, and SESSION_UUID.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    pairs = [(str(t["id"]), t["term"]) for t in terms]
    terms_count = len(pairs)

    post_url = f"https://class.lingco.io/api/vocab_sets/sessions/{SESSION_ID}/responses"

    for run in range(1, 6):
        print(f"--- Run {run} of 5 ---")
        for i, (term_id, term) in enumerate(pairs, start=1):
            time_spent=round(random.uniform(1.5, 6.0), 1)
            payload = {
                "correct": True,
                "level": int(run-1),
                "prompt_in_target": False,
                "prompt_with": "text",
                "respond_in_target": True,
                "respond_with": "text",
                "response": term,
                "scheduled": True,
                "term_id": int(term_id),
                "time_spent": time_spent,
                "type": "multiple_choice"
            }

            post_resp = requests.post(post_url, headers=headers, json=payload)
            status = post_resp.status_code

            if status not in (200, 201):
                print(f"[Run {run} | {i}/{terms_count}] Warning: POST failed with HTTP {status} for Term ID: {term_id}")
                print(f"  Server response: {post_resp.text}")
            else:
                try:
                    post_resp.json()
                    print(f"[Run {run} | {i}/{terms_count}] Posted Term ID: {term_id}, Term: {term}")
                except json.JSONDecodeError:
                    print(f"[Run {run} | {i}/{terms_count}] Warning: non-JSON response for Term ID: {term_id}: {post_resp.text}")

            sleep_time = random.uniform(1.5, 3.0)
            time.sleep(time_spent)

    print("\nAll responses posted!")
    input("\nPress Enter to exit...")

if __name__=="__main__":
    main()
