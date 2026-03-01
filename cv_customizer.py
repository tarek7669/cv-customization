"""
CV Customization module using OpenAI GPT-4.1
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an expert CV/resume writer and career advisor. Your task is to strategically customize a LaTeX CV to maximize relevance for a specific job description.

## ABSOLUTE RULE - HONESTY IS NON-NEGOTIABLE:

**NEVER LIE OR FABRICATE**:
- Do NOT invent skills, experiences, certifications, or qualifications that don't exist in the original CV
- Do NOT add fake projects, companies, or achievements
- Do NOT exaggerate years of experience or proficiency levels beyond what's stated
- You can ONLY work with what the candidate has already provided (both active AND commented-out content)

---

## IMPORTANT: THE CV CONTAINS COMMENTED-OUT CONTENT

The original LaTeX CV may contain **commented-out sections** (lines starting with `%`). These are NOT just notes — they are **real experiences, projects, skills, certifications, and positions** that the candidate has but chose not to include in a previous version.

**You MUST treat commented-out content as part of your available pool:**
- Scan ALL commented-out content for relevant experiences, skills, projects, certifications, etc.
- **UNCOMMENT and USE** any commented-out item that is relevant to the target job description
- Rewrite and adapt uncommented items just like any other content
- These are real, truthful entries — using them is NOT fabrication

---

## YOUR STRATEGIC POWERS - USE THEM WISELY:

### 1. CONTENT SELECTION (Uncomment/Comment Out/Keep)

**UNCOMMENT and ACTIVATE** commented-out items that:
- Are relevant to the target job
- Demonstrate required skills or experience
- Fill gaps in the active CV content for this specific role

**COMMENT OUT (do NOT delete)** active items that:
- Are irrelevant to the target job
- Take up space better used for more relevant content
- Are outdated or less impactful for this role
- Use `%` to comment them out so they remain available for future customizations

**KEEP and ENHANCE** items that:
- Directly align with job requirements
- Demonstrate transferable skills mentioned in the job description
- Show relevant achievements, even if in a different domain

### 2. REWRITING (Adjust Language & Emphasis)

- **Reword** bullet points to use terminology from the job description
- **Emphasize** the aspects of each experience most relevant to the target role
- **Quantify** achievements where possible (if numbers exist in original, highlight them)
- **Adjust** the summary/objective to directly address the role
- **Reorder** bullet points within each experience to lead with the most relevant

### 3. STRUCTURAL CHANGES

- **Reorder sections** based on relevance (put most relevant section first)
- **Reorder items** within sections (most relevant experience first)
- **Condense** less relevant experiences to single lines if keeping them
- **Expand** highly relevant experiences with more detail from the original

### 4. COMMENTING RULES

**When commenting out irrelevant content**, wrap it clearly:
```latex
% --- COMMENTED OUT: Not relevant to this role ---
% \\entry{Old Company}{Old Role}{...}
% \\item Old bullet point
% --- END COMMENTED OUT ---
```

**When uncommenting relevant content**, add a note:
```latex
% ACTIVATED: Relevant to job requirements
```

**NEVER delete any content entirely. Always preserve it as comments.**

---

## LATEX FORMATTING RULES:

- Maintain the original LaTeX structure and formatting commands
- Keep all document class, package imports, and custom commands intact
- Only modify the actual content text, not the LaTeX structure
- Ensure the output is valid, compilable LaTeX (commented-out content should not break compilation)

## LENGTH CONSTRAINT:

- The ACTIVE (uncommented) CV content should be optimized for a maximum of 2 pages
- Commented-out content does not count toward page length
- Use the space freed by commenting out irrelevant content to activate and highlight relevant experience
- Be concise while maintaining impact

## OUTPUT FORMAT:

- Return ONLY the complete LaTeX code
- Do NOT include any explanations outside the LaTeX document
- Start with the document class and end with \\end{document}
- LaTeX comments within the document are expected and encouraged

---

## YOUR MISSION:

Transform this CV into the strongest possible application for this specific role by:
1. Scanning ALL content (active AND commented-out) for relevant material
2. Activating (uncommenting) what helps from the commented pool
3. Commenting out (NOT deleting) what doesn't help
4. Rewriting active content to match the job's language
5. Reordering for maximum impact

All while staying 100% truthful to the candidate's actual experience."""


COMPANY_EXTRACT_PROMPT = """Extract ONLY the company/organization name from the following job description.
Return ONLY the company name as a short, clean string suitable for a filename.
Rules:
- Use lowercase
- Replace spaces with underscores
- Remove special characters (keep only letters, numbers, underscores)
- If you cannot determine the company name, return "company"
- Do NOT include any explanation, just the name

Examples: 'zillow', 'systems_limited', 'google', 'jpmorgan_chase'"""


def _get_client(api_key: str = None) -> OpenAI:
    """Get an OpenAI client using provided key or environment variable."""
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or provide it directly.")
    return OpenAI(api_key=key)


def _clean_response(response_text: str) -> str:
    """Remove markdown code block wrappers if present."""
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # Remove first line (```latex or ```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text


def extract_company_name(job_description: str, api_key: str = None) -> str:
    """
    Extract the company name from a job description using GPT.
    
    Returns:
        A filename-safe company name string (e.g. 'zillow', 'systems_limited')
    """
    try:
        client = _get_client(api_key)
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": COMPANY_EXTRACT_PROMPT},
                {"role": "user", "content": job_description}
            ],
            temperature=0,
            max_tokens=50
        )
        name = response.choices[0].message.content.strip().lower()
        # Extra safety: remove any remaining problematic characters
        name = "".join(c if c.isalnum() or c == "_" else "_" for c in name)
        name = name.strip("_")
        return name if name else "company"
    except Exception:
        return "company"


def customize_cv(latex_cv: str, job_description: str, api_key: str = None) -> str:
    """
    Customize a LaTeX CV based on a job description using OpenAI GPT-4.1.
    
    Args:
        latex_cv: The original LaTeX CV content
        job_description: The target job description
        api_key: OpenAI API key (optional, will use env var if not provided)
    
    Returns:
        The customized LaTeX CV content
    
    Raises:
        ValueError: If inputs are empty or API key is missing
        Exception: If API call fails
    """
    if not latex_cv or not latex_cv.strip():
        raise ValueError("LaTeX CV content cannot be empty")
    
    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty")
    
    client = _get_client(api_key)
    
    user_message = f"""## Original LaTeX CV (includes both active and commented-out content):

```latex
{latex_cv}
```

## Target Job Description:

{job_description}

---

Please customize the CV above to better match this job description. Remember:
- Scan ALL content including commented-out (%) sections for relevant material
- UNCOMMENT relevant commented-out items and rewrite them
- COMMENT OUT (don't delete) irrelevant active items
- NEVER fabricate or lie — only use what the candidate already has
- Rewrite and reorder for maximum impact"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=16000
    )
    
    return _clean_response(response.choices[0].message.content)
