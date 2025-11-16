import streamlit as st
import io
import time
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import inch

# --- Gemini API Setup (Simulated for Immersive Environment) ---
# NOTE: In a real environment, you would use the 'google-genai' library here.
# For this demonstration, we are using a mock implementation.
def generate_cover_letter(job_title, company, skills, experience, tone, job_description):
    """
    Simulates calling the Gemini API to generate a tailored cover letter.
    
    In a real app, this function would handle the API call, payload construction,
    and response processing, including handling citations.
    
    Args:
        ...
        skills (list): A list of skills already split from the input string.
        ...
    """
    # Define the system prompt to ensure the output meets all user requirements
    system_prompt = (
        "You are a professional cover letter generator. Your goal is to write a tailored, "
        "ATS-friendly cover letter in a simple, readable font, avoiding complex tables or graphics. "
        "The letter must be 3-4 distinct paragraphs. "
        "Highlight measurable achievements (use specific numbers/percentages) and explicitly "
        "connect the provided skills to the experience summary and, if present, the job description. "
        "The tone should be: "
    )
    
    # Construct the user query for the model
    user_query = f"""
    Draft a cover letter for the following application:
    - Job Title: {job_title}
    - Company Name: {company}
    - Desired Tone: {tone}
    
    Candidate Highlights:
    - Key Skills to Emphasize: {', '.join(skills)}
    - Experience Summary (Focus on achievements with measurable impact): {experience}
    
    Job Description (If provided, match skills to this text):
    ---
    {job_description if job_description else 'No job description provided.'}
    ---
    
    Begin the letter with a polite salutation (e.g., 'Dear Hiring Team,' or 'Dear [Company Name] Hiring Team,').
    """

    # --- MOCK LLM RESPONSE GENERATION ---
    # This is where the actual LLM call would happen, e.g.:
    # response = client.models.generate_content(...)

    # Generate a mock response based on inputs
    time.sleep(1) # Simulate network delay

    # FIX 1: Accessing the first two skills from the 'skills' list directly
    mock_letter = f"""
    Dear Hiring Team,

    I am writing to express my enthusiastic interest in the **{job_title}** position at **{company}**. Having closely followed {company}'s innovative work in [Relevant Industry], I am highly motivated by the opportunity to contribute my proven track record in {', '.join(skills[:2])}, which align directly with the core demands of this role. My experience is centered on driving tangible results and leveraging technical expertise to achieve business objectives.

    Throughout my career, I have consistently exceeded performance goals by focusing on measurable impact. For instance, in a previous role, I successfully [elaborate on a key achievement from the Experience Summary] resulting in a **[use a number/percentage, e.g., 25%] increase in [metric, e.g., operational efficiency]** and **[use another measurable outcome, e.g., $50,000] in cost savings** over a fiscal year. I am confident in my ability to bring the same level of **{tone}** drive and commitment to excellence to your team, immediately addressing the need for a professional skilled in [another highlighted skill].

    # FIX 2: Joining the full list of skills back into a comma-separated string for display
    My specific technical abilities, including **{', '.join(skills)}**, are perfectly suited to the challenges outlined in the job description, especially in the areas of [mention a specific challenge or requirement]. I excel at translating complex technical requirements into actionable plans and thrive in fast-paced environments where **{tone}** problem-solving is critical. This blend of hands-on skill and strategic thinking positions me as an ideal candidate.

    I am eager for the opportunity to discuss how my background can directly benefit {company}. Thank you for your time and consideration.

    Sincerely,

    [Your Name]
    """

    # Add a fictional name and contact info to make it look professional
    professional_header = (
        "**[Your Name]**\n"
        "[Your Phone Number] | [Your Email Address]\n"
        "[Your LinkedIn/Portfolio URL]\n\n"
    )

    return professional_header + mock_letter.strip()


# --- PDF Generation Function (ReportLab) ---
def create_pdf(cover_letter_text, filename="Cover_Letter.pdf"):
    """
    Creates a PDF from the cover letter text using ReportLab (Platypus for structure).
    This ensures ATS-friendly formatting (no tables, standard structure).
    """
    # Create an in-memory buffer for the PDF
    buffer = io.BytesIO()
    
    # Use SimpleDocTemplate for ATS-friendly flowable document structure
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            leftMargin=0.75 * inch,
                            rightMargin=0.75 * inch,
                            topMargin=0.75 * inch,
                            bottomMargin=0.75 * inch)
    
    Story = []
    
    # Get standard ReportLab styles
    styles = getSampleStyleSheet()
    
    # Define a custom, ATS-friendly paragraph style (Helvetica is a standard font)
    styles.add(ParagraphStyle(name='Body_Justify',
                              fontName='Helvetica',
                              fontSize=10,
                              leading=12,
                              alignment=TA_JUSTIFY))

    styles.add(ParagraphStyle(name='Header',
                              fontName='Helvetica-Bold',
                              fontSize=12,
                              leading=14,
                              spaceAfter=12))

    # Split the cover letter text into paragraphs for flowable processing
    paragraphs = cover_letter_text.split('\n\n')
    
    for para_text in paragraphs:
        if not para_text.strip():
            continue
            
        # Check if it's the professional header section (first few lines)
        is_header = paragraphs.index(para_text) == 0
        
        # ReportLab supports basic HTML-like tags for bold/italic
        # Replace simple '*' or '**' markdown with <b> and <br/>
        
        # FIX: The original replacement `replace('**', '<b>')` caused issues. 
        # We need a robust way to convert pairs of ** to <b> and </b>.
        # Since the input template for the letter body always uses pairs of ** for bolding, 
        # we can use a small function to do the sequential replacement.
        
        html_para = para_text.replace('\n', '<br/>')

        # Sequential replacement to convert Markdown **bold** to <b>bold</b>
        # We replace the first ** with <b> and the second with </b>, and so on.
        
        temp_html_para = []
        in_bold = False
        for chunk in html_para.split('**'):
            if not in_bold:
                temp_html_para.append(chunk)
                in_bold = True
            else:
                temp_html_para.append(f'<b>{chunk}</b>')
                in_bold = False
        
        # Join the list back, removing the extra <b> from the odd-numbered replacements
        html_para = "".join(temp_html_para).replace('<b><b>', '<b>').replace('</b></b>', '</b>')
        
        # Simple fix for the specific header case, since it's always the first element:
        if is_header:
            # The header is simple: "**[Your Name]**\n..."
            # Replace the first two instances of '**' with <b> and </b>
            header_parts = para_text.split('**', 2)
            if len(header_parts) == 3:
                # header_parts[1] is the name. Surround it with bold tags.
                html_para = f"<b>{header_parts[1]}</b><br/>" + header_parts[2].replace('\n', '<br/>')

        
        if is_header:
            p = Paragraph(html_para, styles['Header'])
            Story.append(p)
            Story.append(Spacer(1, 0.25 * inch)) # Add space after header
        else:
            p = Paragraph(html_para, styles['Body_Justify'])
            Story.append(p)
            Story.append(Spacer(1, 0.15 * inch)) # Add space between paragraphs

    try:
        doc.build(Story)
    except Exception as e:
        st.error(f"Error building PDF: {e}")
        return None

    # Get the value of the BytesIO buffer
    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value

# --- Streamlit UI and Logic ---
st.set_page_config(page_title="AI Cover Letter Generator", layout="wide")

st.title("📄 AI-Powered Cover Letter Generator")
st.markdown("Draft and export tailored, ATS-friendly cover letters in seconds.")

# --- User Inputs ---
with st.container(border=True):
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title", "Senior Data Scientist")
        skills = st.text_area("Skills to Highlight (Comma-separated)", "Python, PyTorch, A/B Testing, Cloud Deployment, Statistical Modeling")
    with col2:
        company_name = st.text_input("Company Name", "Gemini Labs")
        tone = st.selectbox("Select Letter Tone", 
                            ['Confident and Strategic', 'Enthusiastic and Collaborative', 
                             'Formal and Results-Driven', 'Creative and Forward-Thinking'])

experience = st.text_area(
    "Experience Summary (Focus on measurable achievements)",
    "Led a team of 3 engineers to optimize ML models, cutting inference time by 40% and saving $10k/month in cloud costs. Built and deployed 5 production-ready systems using Python and Azure, directly impacting 100k users. Mentored junior staff on best practices for PyTorch development."
)

job_description = st.text_area(
    "Optional: Paste Full Job Description (for deeper tailoring)",
    "We are looking for a Senior Data Scientist to lead our core research initiatives. The ideal candidate will have deep expertise in PyTorch, experience deploying models to production environments (Azure/GCP), and a proven ability to mentor junior team members. Must have strong statistical modeling and A/B testing skills."
)

if 'generated_letter' not in st.session_state:
    st.session_state.generated_letter = None
if 'pdf_output' not in st.session_state:
    st.session_state.pdf_output = None

# --- Generation Button ---
if st.button("Generate Cover Letter Draft", type="primary"):
    if job_title and company_name and skills and experience:
        with st.spinner("Drafting your personalized cover letter..."):
            # 1. Generate Text
            letter_draft = generate_cover_letter(
                job_title, company_name, skills.split(', '), experience, tone, job_description
            )
            
            # 2. Create PDF
            pdf_data = create_pdf(letter_draft, f"{company_name}_{job_title}_Cover_Letter.pdf")
            
            # 3. Store in Session State
            st.session_state.generated_letter = letter_draft
            st.session_state.pdf_output = pdf_data
            
            st.success("Drafting complete! Preview available below.")
    else:
        st.error("Please fill in the Job Title, Company Name, Skills, and Experience Summary to generate a draft.")

# --- Output and Download ---
if st.session_state.generated_letter:
    st.subheader("📝 Cover Letter Preview")
    
    # Display the editable text area for quick edits before PDF export
    edited_letter = st.text_area(
        "Edit Draft (This version will be exported to PDF):", 
        st.session_state.generated_letter, 
        height=400
    )

    st.markdown("---")
    
    # Re-generate PDF with edits if text has changed
    if edited_letter != st.session_state.generated_letter:
        st.session_state.generated_letter = edited_letter
        st.session_state.pdf_output = create_pdf(edited_letter, f"{company_name}_{job_title}_Cover_Letter.pdf")
    
    # Check if PDF data is available for download
    if st.session_state.pdf_output:
        st.download_button(
            label="✅ Download Final PDF",
            data=st.session_state.pdf_output,
            file_name=f"{company_name}_{job_title}_{tone.replace(' ', '')}_Cover_Letter.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Could not generate PDF. Please check the content for unsupported characters.")

# Add notes for real-world usage
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Technical Notes:**
    
    This app uses **ReportLab's Platypus** framework to generate an ATS-friendly PDF. 
    The text is formatted using standard Helvetica font and simple paragraphs to ensure 
    compatibility with application tracking systems.
    
    The cover letter generation is powered by a large language model API, 
    simulated here by the `generate_cover_letter` function.
    """
)