name: YouTube Shorts Automation

on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:
    inputs:
      test_mode:
        description: 'Set true to upload now'
        default: 'false'

jobs:
  automation:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      - name: Install System Deps
        run: |
          sudo apt update
          sudo apt install -y ffmpeg fonts-quicksand
      - name: Install Python Deps
        run: |
          # Dodajemy playwright do instalacji
          pip install google-api-python-client google-auth-oauthlib google-auth-httplib2 edge-tts requests gTTS numpy tiktok-uploader playwright
          # Teraz instalacja przeglądarki zadziała
          python -m playwright install chromium
          python -m playwright install-deps chromium
      - name: Restore Secrets
        env:
          TOKEN_DATA: ${{ secrets.YOUTUBE_TOKEN_JSON }}
          CLIENT_DATA: ${{ secrets.CLIENT_SECRETS_JSON }}
          TIKTOK_SESSION_ID: ${{ secrets.TIKTOK_SESSION_ID }}
        run: |
          echo "$TOKEN_DATA" > token.json
          echo "$CLIENT_DATA" > client_secrets.json
          # Tworzymy plik cookies dla biblioteki tiktok-uploader
          echo '[{"name": "sessionid", "value": "'$TIKTOK_SESSION_ID'", "domain": ".tiktok.com", "path": "/"}]' > tiktok_cookies.json
      - name: Run Bot
        env:
          TEST_MODE: ${{ github.event.inputs.test_mode || 'false' }}
          TIKTOK_SESSION_ID: ${{ secrets.TIKTOK_SESSION_ID }}
        run: python src/main.py
      - name: Commit History
        run: |
          git config --local user.email "bot@github.com"
          git config --local user.name "ShortsBot"
          git add assets/used_ids.txt
          git commit -m "Update history [skip ci]" || echo "No changes"
          git push