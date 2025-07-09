import re
import json
import openai

def extract_fields_with_gpt(ocr_text, api_key, model="gpt-4o"):
    openai.api_key = api_key

    if not ocr_text.strip():
        print("⚠️ OCR結果が空だったため、GPTによる抽出をスキップします。")
        return {
            "Full Name": "",
            "Date of Birth": "",
            "Place of Birth": "",
            "Present Address": "",
            "Passport Number": "",
            "Valid Until": "",
            "Category": "",
            "Japan Work Period Start": "",
            "Japan Work Period End": ""
        }

    prompt = f"""
次のBIO DATA形式のテキストから、以下の項目を抽出してください：

- Surname（姓の欄に記載されているもの）
- Given Names（given names欄に記載されている名前すべて）
- Middle Name（ミドルネーム欄に記載されているもの）
- Date of Birth
- Place of Birth
- Present Address
- Passport Number
- Valid Until
- Category（"DANCER"の場合は「舞踏」、"SINGER"の場合は「歌謡」と日本語に翻訳してください）

以下も追加で抽出してください（JAPANに関係ある場合のみ）：
- Japan Work Period Start
- Japan Work Period End

該当がなければ「なし」と返してください。

最後に、"Surname  First Name  Middle Name" の順で2スペースずつ区切った "Full Name" を必ず追加してください。
Middle Name が記載されていない場合でも、空白文字列を使って "Surname  First Name  " のように2スペースを維持してください。

出力形式（JSON形式）：
{{
  "Full Name": "...",
  "Date of Birth": "...",
  "Place of Birth": "...",
  "Present Address": "...",
  "Passport Number": "...",
  "Valid Until": "...",
  "Category": "...",
  "Japan Work Period Start": "...",
  "Japan Work Period End": "..."
}}

テキスト：
{ocr_text}
"""

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "あなたは文書から正確に情報を抽出するアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response['choices'][0]['message']['content']

        if not content.strip():
            print("⚠️ GPT応答が空でした。")
            return {}

        # ```json ブロックを除去
        if content.strip().startswith("```json"):
            content = re.sub(r"^```json\s*", "", content)
            content = re.sub(r"```$", "", content.strip())

        # JSONとして解析
        return json.loads(content)

    except Exception as e:
        print("❌ GPT出力のJSON変換に失敗:", e)
        return {}
