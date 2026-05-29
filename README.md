# ⬡ BPE Tokenizer Explorer: NLP Systems Analysis

An interactive web application and systems analysis project exploring the low-level mechanics of Byte-Pair Encoding (BPE) tokenization used in modern Large Language Models (LLMs). 

<img width="1915" height="727" alt="image" src="https://github.com/user-attachments/assets/e8b335c1-e0b9-4595-98a4-9ef2edc16b95" />
<img width="1787" height="365" alt="image" src="https://github.com/user-attachments/assets/d7b01d87-1a41-44ae-a63c-2ffbb7ef9c89" />




## 🚀 Key Research & Features
* **Tokenization Mechanics:** Custom-trained BPE tokenizers (8K to 256K vocabularies) on the WikiText-2 corpus to analyze compression ratios and character-to-token alignment.
* **Noise Robustness & Perplexity:** Simulated OCR distortion to measure token drift. Demonstrated that raw BPE is brittle, causing a 123% token inflation and a **perplexity spike of +1009** on GPT-2.
* **Fairness & Bias Audit:** Analyzed tokenization consistency across code-mixed (Hindi/Spanish) text, proving a 3.9% fragmentation increase that disproportionately consumes context windows for non-English users.
* **Edge Device Optimization (Systems Engineering):** Designed a custom Python Trie-based tokenizer for low-memory environments, achieving a **99.99% memory reduction** (0.05 KB vs 1877 KB) compared to standard hash dictionaries.

## 🛠️ Tech Stack
* **NLP & Models:** HuggingFace Tokenizers, Transformers (GPT-2)
* **Data & Machine Learning:** Scikit-learn (TF-IDF, Logistic Regression), Pandas, Datasets
* **Web UI:** Streamlit
* **Systems Analysis:** `psutil` (memory benchmarking), Custom Trie Data Structures

## 💻 How to Run Locally
1. Clone the repository:
   `git clone https://github.com/YourUsername/BPE-Tokenizer-Explorer.git`
2. Install the required dependencies:
   `pip install -r requirements.txt`
3. Launch the Streamlit dashboard:
   `streamlit run app.py`
