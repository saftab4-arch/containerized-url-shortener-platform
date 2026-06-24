import os
import random
import string

import psycopg2
import redis
from flask import Flask, jsonify, redirect, request

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "urlshortener"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
    )


def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def generate_code(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            id SERIAL PRIMARY KEY,
            original_url TEXT NOT NULL,
            short_code VARCHAR(20) UNIQUE NOT NULL,
            click_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def home():
    return jsonify(
        {
            "service": "Containerized URL Shortener Platform",
            "version": "v2-watchtower",
            "endpoints": {
                "health": "/health",
                "shorten": "POST /shorten",
                "redirect": "GET /<short_code>",
            },
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "Missing url field"}), 400

    original_url = data["url"]
    short_code = generate_code()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO urls (original_url, short_code) VALUES (%s, %s)",
        (original_url, short_code),
    )

    conn.commit()
    cur.close()
    conn.close()

    r = get_redis_client()
    r.set(short_code, original_url)

    return jsonify(
        {
            "original_url": original_url,
            "short_code": short_code,
            "short_url": f"/{short_code}",
        }
    ), 201


@app.route("/<short_code>")
def redirect_url(short_code):
    r = get_redis_client()
    cached_url = r.get(short_code)

    if cached_url:
        return redirect(cached_url)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT original_url FROM urls WHERE short_code = %s", (short_code,))
    result = cur.fetchone()

    if not result:
        cur.close()
        conn.close()
        return jsonify({"error": "Short URL not found"}), 404

    original_url = result[0]

    cur.execute(
        "UPDATE urls SET click_count = click_count + 1 WHERE short_code = %s",
        (short_code,),
    )

    conn.commit()
    cur.close()
    conn.close()

    r.set(short_code, original_url)

    return redirect(original_url)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000)
