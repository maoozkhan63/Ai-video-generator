from flask import Flask, request, jsonify, send_from_directory, session
from gradio_client import Client
from werkzeug.security import generate_password_hash, check_password_hash
import os
import shutil
import uuid
import sqlite3

app = Flask(__name__)

app.secret_key = "ai-video-generator-secret-key-change-this-later"

client = Client(
    "https://lightricks-ltx-video-distilled.hf.space",
    download_files=True
)

GENERATED_FOLDER = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(GENERATED_FOLDER, exist_ok=True)

DATABASE = os.path.join(os.path.dirname(__file__), "users.db")


def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def files(filename):
    return send_from_directory(".", filename)


@app.route("/generated/<path:filename>")
def generated(filename):
    return send_from_directory(GENERATED_FOLDER, filename)


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "error": "Please fill all fields."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "error": "Password must be at least 6 characters."
        }), 400

    try:
        password_hash = generate_password_hash(password)

        conn = sqlite3.connect(DATABASE)

        conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )

        conn.commit()
        conn.close()

        session["user_email"] = email
        session["user_name"] = name

        return jsonify({
            "success": True,
            "message": "Account created successfully!",
            "name": name
        })

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "error": "This email is already registered."
        }), 400

    except Exception as e:
        print("SIGNUP ERROR:", e)

        return jsonify({
            "success": False,
            "error": "Something went wrong."
        }), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "error": "Please enter email and password."
        }), 400

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_email"] = user["email"]
        session["user_name"] = user["name"]

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "name": user["name"]
        })

    return jsonify({
        "success": False,
        "error": "Invalid email or password."
    }), 401


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })


@app.route("/me")
def me():
    if "user_email" in session:
        return jsonify({
            "logged_in": True,
            "name": session.get("user_name"),
            "email": session.get("user_email")
        })

    return jsonify({
        "logged_in": False
    })


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    prompt = data.get("prompt", "").strip()
    duration = data.get("duration", "5")
    style = data.get("style", "cinematic")

    if not prompt:
        return jsonify({
            "error": "Please enter a video idea."
        }), 400

    style_prompts = {
        "cinematic": "cinematic, dramatic lighting, professional film look",
        "realistic": "photorealistic, realistic details, natural lighting",
        "anime": "anime style, detailed anime artwork, vibrant visuals",
        "3d": "high quality 3D animation, detailed 3D graphics",
        "action": "dynamic action scene, dramatic movement, energetic visuals"
    }

    style_text = style_prompts.get(
        style,
        style_prompts["cinematic"]
    )

    final_prompt = f"{style_text}. {prompt}"

    try:
        result = client.predict(
            final_prompt,
            "worst quality, blurry, distorted, jittery",
            None,
            None,
            512,
            704,
          "text-to-video",
float(duration),
9,
42,
True,
1,
True,
api_name="/text_to_video"
        )

        generated = result[0]

        if isinstance(generated, dict):

            if "video" in generated:
                video_data = generated["video"]

                if isinstance(video_data, dict):
                    video_path = video_data.get("path")
                    video_url = video_data.get("url")
                else:
                    video_path = video_data
                    video_url = None

            else:
                video_path = generated.get("path")
                video_url = generated.get("url")

        else:
            video_path = generated
            video_url = None

        if video_url and str(video_url).startswith("http"):
            return jsonify({
                "success": True,
                "video": video_url
            })

        if not video_path or not os.path.exists(str(video_path)):
            return jsonify({
                "success": False,
                "error": "Video file nahi mili."
            }), 500

        filename = f"video_{uuid.uuid4().hex}.mp4"

        destination = os.path.join(
            GENERATED_FOLDER,
            filename
        )

        shutil.copy2(
            str(video_path),
            destination
        )

        return jsonify({
            "success": True,
            "video": f"/generated/{filename}"
        })

    except Exception as e:
        print("ERROR:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )