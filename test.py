from pathlib import Path
import json

root = Path.cwd()

# Remove the temporary pyproject.toml created for Vercel
pyproject = root / "pyproject.toml"

if pyproject.exists():
    pyproject.unlink()
    print("Removed pyproject.toml")

# Create vercel.json
vercel_config = {
    "builds": [
        {
            "src": "backend/app/main.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "backend/app/main.py"
        }
    ]
}

vercel_json = root / "vercel.json"
vercel_json.write_text(
    json.dumps(vercel_config, indent=2),
    encoding="utf-8"
)

print(f"Created: {vercel_json}")
print("Vercel configured to use:")
print("backend/app/main.py")