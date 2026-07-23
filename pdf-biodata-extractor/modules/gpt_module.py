import re
import json
from openai import OpenAI


def extract_fields_with_gpt(ocr_text, api_key, model="gpt-5-mini"):

    client = OpenAI(api_key=api_key)

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
            "Japan Work Periods": "",
            "Japan Entry Count": 0,
            "Japan Work Period Start": "",
            "Japan Work Period End": "",
            "Philippines Work Periods": ""
        }

    prompt = f"""
次のBIO DATA形式のテキストから、以下の項目を抽出してください。

必須で抽出する項目：
- Surname（姓の欄に記載されているもの）
- Given Names（given names欄に記載されている名前すべて）
- Middle Name（ミドルネーム欄に記載されているもの）
- Date of Birth
- Place of Birth
- Present Address
- Passport Number
- Valid Until
- Category（"DANCER"の場合は「舞踏」、"SINGER"の場合は「歌謡」と日本語に翻訳してください。それ以外は原文のまま。）

Employment Records 等に記載されている全ての職歴について、勤務期間を抽出し、次のルールで分類してください。

1) 日本での経歴（Japan Work Periods）
- 日本国内での勤務と判断できるものを対象とします（住所に "JAPAN" や日本の都道府県名、都市名が含まれる場合など）。
- 該当する全ての勤務期間を、古い順から新しい順に並べて列挙してください。
- 各行には "APRIL 19, 2025 TO JULY 19, 2025" のように期間だけを書いてください（店名などは含めないでください）。
- それらを1行に1件ずつ、改行区切りの1つの文字列として "Japan Work Periods" に入れてください。
- 日本での経歴が1件も無い場合は "Japan Work Periods" を「なし」としてください。
- "Japan Entry Count"、"Japan Work Period Start"、"Japan Work Period End" はプログラム側で設定するので、ここでは "Japan Entry Count": 0、"Japan Work Period Start": ""、"Japan Work Period End": "" としてください。

2) フィリピンでの経歴（Philippines Work Periods）
- 上記の日本以外の全ての経歴を対象とします（フィリピン国内の経歴を想定）。
- 各経歴から勤務期間（"〜 TO 〜" 形式の日付部分）だけを抜き出してください。
- それらを古い順から新しい順に並べ、1行に1件ずつ、改行区切りの1つの文字列として "Philippines Work Periods" に入れてください。
- フィリピンでの経歴が1件も無い場合は「なし」としてください。

注意事項：
- 日付の書式は、入力に使われている英語表記（例: "MAY 8, 2016" や "July 3, 2024"）を維持してください。
- OCR特有の誤認（0とO, 1とI, 8とBなど）は文脈に応じて補正してください。
- 出力は説明文などを一切含めず、有効なJSONオブジェクトのみを返してください。
- コードブロック（```json や ```）も絶対に出力しないでください。

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
  "Japan Work Periods": "...",
  "Japan Entry Count": 0,
  "Japan Work Period Start": "",
  "Japan Work Period End": "",
  "Philippines Work Periods": "..."
}}

テキスト：
{ocr_text}
"""

    try:
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": "あなたは文書から正確に情報を抽出するアシスタントです。出力は常に有効なJSONだけを返してください。"
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
        )

        content = getattr(response, "output_text", None)

        if not content:
            texts = []
            for item in getattr(response, "output", []):
                for c in getattr(item, "content", []):
                    text_obj = getattr(c, "text", None)
                    if text_obj:
                        if hasattr(text_obj, "value"):
                            texts.append(text_obj.value)
                        else:
                            texts.append(str(text_obj))
            content = "\n".join(texts)

        if not content or not content.strip():
            print("⚠️ GPT応答が空でした。")
            return {}

        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"```$", "", text.strip())

        return json.loads(text)

    except Exception as e:
        print("❌ GPT出力のJSON変換またはAPI呼び出しに失敗:", e)
        return {}
