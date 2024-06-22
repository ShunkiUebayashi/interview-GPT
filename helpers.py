import openai


def make_prompt_summary(theme, dialog, summary):
    if len(summary) > 0:
        return f"""以下はテーマ：{theme}についてのこれまでの対話についての要約および直近の対話です。
要約 : {summary}
対話 : {dialog}
この2つを組み合わせて新しい要約を作成してください。
キーポイントとなる部分については個別に要約しても構いません。
また、テーマ：{theme}に強く関連する部分を必ず含めて要約してください。"""
    else:
        return f"""以下はテーマ：{theme}についてのこれまでの対話です。
対話 : {dialog}
この対話を要約してください。
キーポイントとなる部分については個別に要約しても構いません。
また、テーマ：{theme}に強く関連する部分を必ず含めて要約してください。
逆に、テーマ：{theme}に関連しない部分は含めないようにしてください。"""


def generate(model, prompt):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].message["content"].strip()


def generate_top_low(model, prompt):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].message["content"].strip()


def summarize(model, theme, conversation_history, summary):
    dialog = "\n".join(
        [
            f"{'面接官: ' if conv['role'] == 'assistant' else 'ユーザ: '}{conv['content']}"
            for conv in conversation_history
        ]
    )
    prompt = make_prompt_summary(theme, dialog, summary)
    return generate(model, prompt)


def senetence_juding(theme, summary, dialog):
    print(summary)
    print(dialog)
    if len(summary) > 0:
        return f"""テーマとこれまでの対話の要約、直近の対話が与えられるので、対話がテーマから逸脱しているかどうかを判定してください。逸脱していれば「逸脱」と回答し、そうでなければ「関連」と回答してください。
テーマ : {theme}
要約 : {summary}
対話 : {dialog}
=>この対話文はテーマ：{theme}から逸脱していますか?
回答は「逸脱」か「関連」の一語のみで行い、それ以外の説明は行わないようにしてください。"""
    else:
        return f"""テーマと対話が与えられるので、対話がテーマから逸脱しているかどうかを判定してください。逸脱していれば「逸脱」と回答し、そうでなければ「関連」と回答してください。
テーマ : {theme}
対話 : {dialog}
=>この対話文はテーマ：{theme}から逸脱していますか?
回答は「逸脱」か「関連」の一語のみで行い、それ以外の説明は行わないようにしてください。"""


def judge(model, theme, summary, conversation_history):
    recent_dialog = "\n".join(
        [
            f"{'面接官: ' if conv['role'] == 'assistant' else 'ユーザ: '}{conv['content']}"
            for conv in conversation_history[-10:]
        ]
    )
    prompt = senetence_juding(theme, summary, recent_dialog)
    return generate_top_low(model, prompt)


def result_judging(result):
    if "逸脱" in result and "関連" not in result:
        return 1
    elif "逸脱" not in result and "関連" in result:
        return 0
    else:
        return -1


def generate_question(model, theme, summary, recent_dialog):
    prompt = f"""以下はテーマ：{theme}についての対話です。要約と直近の対話に基づいて、テーマに関連する質問をしてください。
{recent_dialog}
質問 :"""
    return generate(model, prompt)
