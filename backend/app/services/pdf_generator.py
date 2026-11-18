from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def render_pdf(config, paper_set, answer_key=False):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ExamTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=14, leading=18))
    styles.add(ParagraphStyle(name="Question", parent=styles["BodyText"], fontSize=10, leading=14, spaceAfter=8))
    story = [
        Paragraph(escape(config.organization.upper()), styles["ExamTitle"]),
        Paragraph(escape(config.exam_name), styles["Heading2"]),
        Paragraph(f"Subject: {escape(config.subject)} &nbsp;&nbsp; Set: {paper_set['set_name']}", styles["BodyText"]),
        Paragraph(f"Duration: {config.duration_minutes} minutes &nbsp;&nbsp; Maximum Marks: {config.max_marks}", styles["BodyText"]),
        Spacer(1, 8)
    ]
    if not answer_key:
        story += [Paragraph("General Instructions", styles["Heading3"]), Paragraph(escape(config.instructions), styles["BodyText"]), Spacer(1, 8)]
    for section in paper_set["sections"]:
        story.append(Paragraph(escape(section["name"]), styles["Heading2"]))
        for idx, q in enumerate(section["questions"], 1):
            body = f"<b>Q{idx}.</b> {escape(q.get('question',''))}"
            if answer_key:
                body += f"<br/><b>Answer:</b> {escape(str(q.get('correct_answer','')))}"
            else:
                body += f" &nbsp; <b>[{q['marks']} marks]</b>"
                if q.get("type") == "mcq":
                    body += "<br/>" + "<br/>".join(f"({chr(65+i)}) {escape(str(o))}" for i, o in enumerate(q.get("options", [])))
            story.append(Paragraph(body, styles["Question"]))
    doc.build(story)
    return buffer.getvalue()
