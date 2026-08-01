import os
import json
import gradio as gr
from dotenv import load_dotenv

from src.core.orchestrator import Orchestrator
from src.core.coordinator import ReviewCoordinator

load_dotenv()

orchestrator = Orchestrator()
coordinator = ReviewCoordinator(orchestrator.cover, orchestrator.net)

# Global in-memory state dictionary for Gradio session
current_session_state = {}

def process_generate(cv_file, job_url, manual_jd, mode):
    global current_session_state
    
    if not cv_file:
        return (
            "⚠️ Please upload your CV in PDF format.",
            None,
            "",
            "",
            "⚠️ Missing CV PDF"
        )

    cv_path = cv_file.name if hasattr(cv_file, "name") else cv_file

    try:
        res = orchestrator.route(
            option=mode,
            cv_pdf_path=cv_path,
            job_url=job_url,
            jd_text_optional=manual_jd
        )
        current_session_state = res
        
        status_msg = f"✅ Task completed successfully for mode '{mode}'!"
        if res.get("needs_jd_text"):
            status_msg += " (Note: Job webpage returned minimal text; used manual description)."

        # Format output displays based on mode
        letter_out = res.get("letter") or ""
        pdf_out = res.get("pdf_path")
        
        msgs = res.get("messages")
        msgs_out = ""
        if msgs:
            msgs_out = f"### 💬 LinkedIn DM / Referral Request\n\n{msgs.get('referral_request', '')}\n\n---\n\n### 📧 Cold Email\n\n{msgs.get('cold_email', '')}"

        review = res.get("review")
        review_out = ""
        if review:
            review_out = f"### 📊 Verdict: {review.get('verdict', 'N/A')} (Confidence: {int(review.get('overall_confidence', 0)*100)}%)\n\n"
            
            summary = review.get("summary_analysis", {})
            review_out += f"**Strengths:** {summary.get('strengths', '')}\n\n"
            review_out += f"**Weaknesses:** {summary.get('weaknesses', '')}\n\n"
            review_out += f"**Strategic Angle:** {summary.get('strategic_angle', '')}\n\n"

            kw = review.get("keyword_optimization", {})
            review_out += f"**Missing Keywords (ATS):** {', '.join(kw.get('missing_keywords', []))}\n\n"

            review_out += "### 💡 Prioritized Action Edits:\n"
            for edit in review.get("prioritized_edits", []):
                review_out += f"- **[{edit.get('priority')}] {edit.get('section')}**: {edit.get('suggestion')}\n"
                review_out += f"  *Reasoning:* {edit.get('reasoning')}\n"
                for bullet in edit.get("example_bullets", []):
                    review_out += f"  *Example:* `{bullet}`\n"

        return letter_out, pdf_out, msgs_out, review_out, status_msg

    except Exception as e:
        return "", None, "", "", f"❌ Error executing task: {e}"


def process_revision(satisfaction, feedback_text):
    global current_session_state

    if not current_session_state:
        return "", None, "", "⚠️ No active session found. Please run generation first."

    try:
        updated_state = coordinator.handle(current_session_state, satisfaction, feedback_text)
        current_session_state = updated_state

        status_msg = updated_state.get("status_message", "Updated.")

        letter_out = updated_state.get("letter") or ""
        pdf_out = updated_state.get("pdf_path")

        msgs = updated_state.get("messages")
        msgs_out = ""
        if msgs:
            msgs_out = f"### 💬 LinkedIn DM / Referral Request\n\n{msgs.get('referral_request', '')}\n\n---\n\n### 📧 Cold Email\n\n{msgs.get('cold_email', '')}"

        return letter_out, pdf_out, msgs_out, status_msg

    except Exception as e:
        return "", None, "", f"❌ Error processing revision: {e}"


# Build Gradio UI Dashboard
theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="blue",
    neutral_hue="slate"
)

with gr.Blocks(theme=theme, title="Multi-Agent AI Job Hunt Assistant") as demo:
    gr.Markdown(
        """
        # 🤖 Multi-Agent AI Job Hunt Assistant
        *Automate cover letters, networking outreach, and ATS CV reviews using specialized collaborative AI agents.*
        """
    )

    with gr.Row():
        with gr.Column(scale=4):
            cv_input = gr.File(label="📄 Upload CV (PDF format)", file_types=[".pdf"])
            job_url_input = gr.Textbox(
                label="🔗 Job Posting URL",
                placeholder="https://www.linkedin.com/jobs/view/123456789/ or Greenhouse/Lever link...",
                lines=1
            )
            manual_jd_input = gr.Textbox(
                label="📝 Optional Job Description Text (Fallback if URL is gated)",
                placeholder="Paste job title & requirements here if scraping is restricted...",
                lines=4
            )
            mode_input = gr.Radio(
                choices=["cover_letter", "networking", "cv_review"],
                value="cover_letter",
                label="🎯 Select Agent Task",
                info="Choose what you want the multi-agent team to produce."
            )
            generate_btn = gr.Button("🚀 Run AI Agent Team", variant="primary", size="lg")

        with gr.Column(scale=6):
            status_box = gr.Markdown("##### System Status: Ready")
            
            with gr.Tabs():
                with gr.TabItem("✉️ Cover Letter"):
                    cover_output = gr.Markdown(label="Generated Cover Letter")
                    pdf_download = gr.File(label="📥 Download Cover Letter PDF")

                with gr.TabItem("💬 Networking Outreach"):
                    networking_output = gr.Markdown(label="LinkedIn DM & Cold Email Templates")

                with gr.TabItem("📊 CV & ATS Review"):
                    review_output = gr.Markdown(label="ATS Analysis & Recruiter Verdict")

            gr.Markdown("---")
            gr.Markdown("### 🔁 Human-in-the-Loop Feedback & Revisions")
            with gr.Row():
                satisfaction_radio = gr.Radio(
                    choices=["No - Request Revision", "Yes - Satisfied"],
                    value="No - Request Revision",
                    label="Are you satisfied with the generated output?"
                )
            feedback_input = gr.Textbox(
                label="Feedback / Revision Requests",
                placeholder="e.g., 'Make the cover letter focus more on distributed systems leadership', 'Make cold email tone warmer'",
                lines=2
            )
            revise_btn = gr.Button("🔁 Apply Revision", variant="secondary")

    # Wire event handlers
    generate_btn.click(
        fn=process_generate,
        inputs=[cv_input, job_url_input, manual_jd_input, mode_input],
        outputs=[cover_output, pdf_download, networking_output, review_output, status_box]
    )

    revise_btn.click(
        fn=process_revision,
        inputs=[satisfaction_radio, feedback_input],
        outputs=[cover_output, pdf_download, networking_output, status_box]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
