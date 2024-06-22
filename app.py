import openai
import openai.error
from flask import Flask, flash, redirect, render_template, request, session, url_for

from helpers import (
    generate,
    generate_question,
    generate_top_low,
    judge,
    make_prompt_summary,
    result_judging,
    senetence_juding,
    summarize,
)

app = Flask(__name__)
app.secret_key = "your_secret_key"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        session["api_key"] = request.form["api_key"]
        session["model"] = request.form["model"]
        session["theme"] = request.form["theme"]
        return redirect(url_for("main"))
    return render_template("settings.html")


@app.route("/main", methods=["GET", "POST"])
def main():
    if "api_key" not in session:
        return redirect(url_for("settings"))

    if request.method == "POST":
        if "reset" in request.form:
            session.pop("conversations", None)
            session.pop("results", None)
            session.pop("summary", None)
            session.pop("full_conversation_history", None)
            flash("チャットがリセットされました。")
            return redirect(url_for("main"))

        if "evaluate" in request.form:
            session["conversations"].append(
                {
                    "role": "user",
                    "content": f"この対話は{session['theme']}の対話です。一連の面接の対話を評価してください。",
                }
            )
            api_key = session["api_key"]
            model = session["model"]
            theme = session["theme"]

            # Initialize OpenAI API
            openai.api_key = api_key

            all_conversations = "\n".join(
                [
                    f"{'面接官' if conv['role'] == 'assistant' else 'ユーザ'}: {conv['content']}"
                    for conv in session["full_conversation_history"]
                ]
            )
            prompt = f"以下はテーマ：{theme}に関する一連の面接の対話です。この対話を評価してください。\n\n{all_conversations}"
            evaluation = generate(model, prompt)
            return render_template(
                "evaluation.html",
                evaluation=evaluation,
                conversations=session.get("full_conversation_history", []),
                results=session.get("results", []),
            )

        user_message = request.form["message"]
        if user_message.lower() == "exit":
            return render_template(
                "results.html", conversations=session["full_conversation_history"], results=session["results"]
            )

        api_key = session["api_key"]
        model = session["model"]
        theme = session["theme"]

        # Initialize OpenAI API
        openai.api_key = api_key

        dialog = user_message
        summary = session.get("summary", "")

        if "full_conversation_history" not in session:
            session["full_conversation_history"] = []

        # Save the full conversation history
        session["full_conversation_history"].append({"role": "user", "content": user_message, "deviation": None})

        try:
            jd = judge(model, theme, summary, dialog)
            rj = result_judging(jd)

            # Save deviation result
            session["full_conversation_history"][-1]["deviation"] = jd

            # Determine if it's time to summarize
            turn_count = len(session["full_conversation_history"]) // 2
            if turn_count >= 15 and turn_count % 15 == 0:
                summary = summarize(model, theme, dialog, summary)
                session["summary"] = summary

            if "conversations" not in session:
                session["conversations"] = []

            if "results" not in session:
                session["results"] = []

            session["conversations"].append({"role": "user", "content": user_message})
            session["results"].append({"dialog": dialog, "result": jd})

            # Generate the next response based on summary and recent dialog
            if turn_count < 15 or turn_count % 15 != 0:
                recent_dialog = "\n".join(
                    [
                        f"{'面接官' if conv['role'] == 'assistant' else 'ユーザ'}: {conv['content']}"
                        for conv in session["full_conversation_history"][-10:]
                    ]
                )
            else:
                recent_dialog = f"要約: {summary}\n" + "\n".join(
                    [
                        f"{'面接官' if conv['role'] == 'assistant' else 'ユーザ'}: {conv['content']}"
                        for conv in session["full_conversation_history"][-10:]
                    ]
                )

            response = generate_question(model, theme, summary, recent_dialog)
            session["conversations"].append({"role": "assistant", "content": response})

            # Save the assistant response to the full conversation history
            session["full_conversation_history"].append({"role": "assistant", "content": response, "deviation": None})

            # デバッグ用の出力を追加
            print("Full Conversation History:", session["full_conversation_history"])

            # Ensure the session is saved
            session.modified = True

        except openai.error.RateLimitError:
            flash("APIのリクエスト制限を超過しました。しばらくしてから再試行してください。")
        except openai.error.InvalidRequestError as e:
            flash(f"無効なリクエスト: {e}")
        except openai.error.OpenAIError as e:
            flash(f"OpenAI APIエラー: {e}")

    return render_template(
        "main.html", conversations=session.get("full_conversation_history", []), results=session.get("results", [])
    )


if __name__ == "__main__":
    app.run(debug=True)
