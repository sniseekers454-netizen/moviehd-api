from flask import Flask, jsonify, request
from flask_cors import CORS
from m3u8 import get_m3u8

app = Flask(__name__)
CORS(app)

print("🚀 M3U8 API running")
print("📡 Endpoint: GET /api/m3u8?url=")


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "service": "moviehd m3u8 api",
        "endpoint": "/api/m3u8?url="
    })


@app.route("/api/m3u8", methods=["GET"])
def api_m3u8():
    video_url = request.args.get("url")

    if not video_url:
        return jsonify({
            "status": "error",
            "message": "Missing ?url= parameter",
            "m3u8": None
        }), 400

    result = get_m3u8(video_url)

    # 🔒 ALWAYS return JSON
    if not result or not result.get("m3u8"):
        return jsonify({
            "status": "error",
            "source_url": video_url,
            "m3u8": None
        }), 200

    return jsonify({
        "status": "ok",
        "source_url": video_url,
        "m3u8": result["m3u8"]
    })


# ❌ DO NOT use app.run()
# Gunicorn runs this on Render
