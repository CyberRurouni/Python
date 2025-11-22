from libraries import json, genai

client = genai.Client(api_key="AIzaSyCTGNS9wsaHctjxpiHeBE-BVAO2Ljefl5M")

section = "home feeds"


def recieve_post_info(post_info):
    # Convert list of spans into JSON string
    return json.dumps(post_info, indent=2)


def decide_interest(info_str):
    prompt = f"""
Hey there! I want to simulate actual browsing behavior on Instagram 
to avoid being flagged as a bot. 
I will provide you info like on which section I am, is it home feeds, reels, or explore section.
Based on that info, you are expected to act like I would do,
I am someone who is drawn to science, technology, and technical info.
But let us narrow it down:
For Science: I like Physics and Maths.
For Technology: I like AI.
For Technical Info: I like AI related info, like its progress and innovation done by it.
I want you to act like me, and interact with posts, reels, and stories based on my interests (the one I just provided).
You are expected to scroll past other posts and reels that do not interest me.

Input: {info_str} Note that you are expected to extract preview of post from this info, and then decide if I would be interested in it or not.
Output: {{
    "answer": "Yes" or "No"
}}
(Output must be **strict JSON only**.)
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)

    raw_text = response.text.strip()

    # Clean markdown wrappers if Gemini adds them
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")  # remove ```
        if raw_text.startswith("json"):
            raw_text = raw_text[4:].strip()  # remove leading 'json'

    try:
        result = json.loads(raw_text)
        if result.get("answer") in ["Yes", "No"]:
            return result["answer"]
        else:
            print("AI returned unexpected format:", result)
            print("Receding to Default Answer")
            return "No"
    except json.JSONDecodeError:
        return "No"
