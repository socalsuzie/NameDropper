import streamlit as st
import openai
from PIL import Image
import io
import base64
import pandas as pd
import re

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🎨 Namedropper: Batch Art Titler")
st.write("Upload multiple images of your artwork. Unique names will be generated for each, except for obvious pairs or series (based on filenames for now).")

uploaded_files = st.file_uploader("Upload image files", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

def extract_base_group(filename):
    return re.sub(r'[_-]?\d+\.\w+$', '', filename).lower()

def generate_title(image_bytes):
    img_b64 = base64.b64encode(image_bytes).decode()

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "You are a sophisticated art expert naming artwork for a gallery. Generate a unique and elegant title for each image."},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
            ]}
        ],
        max_tokens=50,
    )

    return response["choices"][0]["message"]["content"].strip()

if uploaded_files:
    progress = st.progress(0)
    results = []
    group_titles = {}

    for i, uploaded_file in enumerate(uploaded_files):
        image_bytes = uploaded_file.read()
        group_key = extract_base_group(uploaded_file.name)

        if group_key in group_titles:
            base_title = group_titles[group_key]
        else:
            base_title = generate_title(image_bytes)
            group_titles[group_key] = base_title

        # Count number already assigned with this group_key
        count = sum(1 for f in results if extract_base_group(f[0]) == group_key)
        final_title = f"{base_title} {count + 1}" if count > 0 else base_title

        results.append([uploaded_file.name, final_title])
        progress.progress((i + 1) / len(uploaded_files))

    df = pd.DataFrame(results, columns=["Filename", "Generated Title"])
    st.success("🎉 Done! Download your CSV below.")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "namedropper_titles.csv", "text/csv")
