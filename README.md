# AI Auto-Category & Tag Generator
**Powered by Google Gemini 2.5 Flash**

A sophisticated E-commerce Product Intelligence tool that automates categorization, SEO tag generation, and sustainability filtering using advanced Generative AI.

---

## Architecture Overview
This project is built with a focus on **Clean Architecture** and **Separation of Concerns** to ensure scalability and reliability:

* **`/api`**: The web layer handling RESTful routing and request/response cycles.
* **`/lib`**: The core logic layer containing the `GeminiEngine`. It handles AI integration, retry logic, and fuzzy string matching.
* **`/models`**: Data integrity layer using Pydantic-style schemas to enforce **Structured AI Outputs**.
* **`/prompts`**: Externalized prompt management, keeping the "AI instructions" separate from the execution code.
* **`/app`**: A responsive, dark-themed frontend dashboard for a seamless user experience.

---

## 🧠 AI Prompt Design & Logic
To achieve **Business Logic Grounding** and **Practical Usefulness**, the following strategies were implemented:

1.  **System Instructioning**: The AI is strictly role-played as a "Senior E-commerce Catalog Manager" to ensure professional and accurate metadata.
2.  **Structured JSON Enforcement**: Uses Gemini's `response_mime_type: "application/json"` to guarantee the output perfectly matches the expected frontend schema.
3.  **Fuzzy Category Matching**: Includes a custom **Levenshtein Distance** algorithm. If the AI suggests a category slightly outside our predefined list (e.g., "Electronics" vs "Electronic"), the system automatically corrects it to the valid business category.
4.  **Sustainability Extraction**: The prompt is engineered to identify specific eco-friendly attributes (Biodegradable, Vegan, Recycled) directly from raw product descriptions.
5.  **Robust Error Handling**: Built-in exponential backoff and retry logic to handle API rate limits (429 errors) gracefully.

---

## Technical Requirements Met
* ✅ **Structured JSON Outputs**: Validated against internal models.
* ✅ **Environment-based API Management**: Uses `.env` for secure key handling (excluded from GitHub for security).
* ✅ **Prompt & Response Logging**: Full traceability in `logs/app.log`.
* ✅ **Clean Code**: Strict modularity between the AI engine and the API routes.

---

## Local Setup
1. **Clone the repo**:
   ```bash
   git clone https://github.com/VikashBaibhav/AI-Auto-Category-Tag-Generator

2. **Install dependencies**:
  ```bash
pip install -r requirements.txt

```


3. **Configure Environment**:
Create a `.env` file in the root directory and add your key:
```text
GEMINI_API_KEY=your_api_key_here

```

4. **Run Application**:
```bash
python run.py

```
