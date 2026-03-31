from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Domain colors
HEALTH = colors.HexColor('#22C55E')
RELATIONSHIPS = colors.HexColor('#A855F7')
WORK = colors.HexColor('#3B82F6')
PLAY = colors.HexColor('#F97316')

# Theme colors
BG = colors.HexColor('#0A0A0F')
SURFACE = colors.HexColor('#1A1A2E')
TEXT_PRIMARY = colors.white
TEXT_MUTED = colors.HexColor('#94A3B8')
ACCENT = colors.HexColor('#22C55E')
DANGER = colors.HexColor('#EF4444')

def create_executive_summary():
    c = canvas.Canvas("D:/Projects/Project-Management/docs/Tony_Career_Clarity_Summary.pdf", pagesize=letter)
    width, height = letter

    # === PAGE 1: SITUATION & RECOMMENDATION ===

    # Dark background
    c.setFillColor(BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Header gradient bar
    c.setFillColor(WORK)
    c.rect(0, height - 50, width, 50, fill=True, stroke=False)

    # Domain color stripe at top
    stripe_width = width / 4
    c.setFillColor(HEALTH)
    c.rect(0, height - 6, stripe_width, 6, fill=True, stroke=False)
    c.setFillColor(RELATIONSHIPS)
    c.rect(stripe_width, height - 6, stripe_width, 6, fill=True, stroke=False)
    c.setFillColor(WORK)
    c.rect(stripe_width * 2, height - 6, stripe_width, 6, fill=True, stroke=False)
    c.setFillColor(PLAY)
    c.rect(stripe_width * 3, height - 6, stripe_width, 6, fill=True, stroke=False)

    # Title
    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - 38, "Tony's Career Clarity Executive Summary")

    # Date
    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 68, "January 14, 2026")

    # Current Situation Box
    c.setFillColor(SURFACE)
    c.roundRect(36, height - 200, width - 72, 120, 8, fill=True, stroke=False)
    c.setStrokeColor(WORK)
    c.setLineWidth(2)
    c.roundRect(36, height - 200, width - 72, 120, 8, fill=False, stroke=True)

    c.setFillColor(WORK)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 100, "CURRENT SITUATION")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica", 11)
    y = height - 125
    lines = [
        "Day 14 of full-time AI career (quit serving Jan 1, 2026)",
        "Current income: $500/mo from AI Foundations only",
        "30th birthday: February 7, 2026 | Canada speaking gig: March 2026",
        "Savings depleted, rent due February - limited runway"
    ]
    for line in lines:
        c.drawString(50, y, line)
        y -= 18

    # THE VERDICT Box
    c.setFillColor(SURFACE)
    c.roundRect(36, height - 360, width - 72, 140, 8, fill=True, stroke=False)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(3)
    c.roundRect(36, height - 360, width - 72, 140, 8, fill=False, stroke=True)

    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 240, "THE VERDICT: BJJ Intelligence First")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica", 11)
    y = height - 270
    verdict_lines = [
        "Score: 48/50 - Highest rated opportunity",
        "Zero conflict with AI Foundations (different audience entirely)",
        "Combines two loves: BJJ (first love) + AI (second love)",
        "Unique market position - no one else doing BJJ + AI fusion",
        "Blue belt credibility - taps black belts, can teach from experience"
    ]
    for line in verdict_lines:
        c.drawCentredString(width/2, y, line)
        y -= 18

    # Opportunity Rankings
    c.setFillColor(RELATIONSHIPS)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 400, "OPPORTUNITY RANKINGS")

    # Rankings table
    rankings = [
        ("1. BJJ Intelligence", "BUILD", ACCENT),
        ("2. Freelance Clients", "PURSUE", WORK),
        ("3. Canada Speaking", "PREPARE", RELATIONSHIPS),
        ("4. AI Foundations", "MAINTAIN", WORK),
        ("5. AI Lunchbox", "DEFER", PLAY),
        ("6. Jasen Partnership", "DECLINE", DANGER),
    ]

    y = height - 425
    for name, action, color in rankings:
        c.setFillColor(TEXT_PRIMARY)
        c.setFont("Helvetica", 10)
        c.drawString(60, y, name)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(220, y, action)
        y -= 18

    # Target metrics box
    c.setFillColor(SURFACE)
    c.roundRect(320, height - 540, 230, 100, 8, fill=True, stroke=False)
    c.setStrokeColor(PLAY)
    c.setLineWidth(2)
    c.roundRect(320, height - 540, 230, 100, 8, fill=False, stroke=True)

    c.setFillColor(PLAY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(335, height - 455, "TARGET METRICS")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(435, height - 495, "$10K MRR")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 10)
    c.drawCentredString(435, height - 520, "Ultimate goal: 6-12 months")

    # Footer
    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, 30, "Page 1 of 3 | Career Clarity Analysis - January 2026")

    c.showPage()

    # === PAGE 2: 90-DAY ACTION PLAN ===

    # Dark background
    c.setFillColor(BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Header
    c.setFillColor(PLAY)
    c.rect(0, height - 50, width, 50, fill=True, stroke=False)

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 35, "90-Day Action Plan")

    # Phase 1 Box
    c.setFillColor(SURFACE)
    c.roundRect(36, height - 230, width/2 - 54, 160, 8, fill=True, stroke=False)
    c.setStrokeColor(DANGER)
    c.setLineWidth(2)
    c.roundRect(36, height - 230, width/2 - 54, 160, 8, fill=False, stroke=True)

    c.setFillColor(DANGER)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 88, "PHASE 1: IMMEDIATE (Weeks 1-2)")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica", 10)
    phase1_tasks = [
        "Send Jasen decline message",
        "Create freelance profiles",
        "Land 1-2 small clients",
        "Maintain AiF commitments",
        "Outline BJJ Intelligence"
    ]
    y = height - 115
    for task in phase1_tasks:
        c.drawString(55, y, f"• {task}")
        y -= 18

    # Phase 2 Box
    c.setFillColor(SURFACE)
    c.roundRect(width/2 + 18, height - 230, width/2 - 54, 160, 8, fill=True, stroke=False)
    c.setStrokeColor(WORK)
    c.setLineWidth(2)
    c.roundRect(width/2 + 18, height - 230, width/2 - 54, 160, 8, fill=False, stroke=True)

    c.setFillColor(WORK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(width/2 + 32, height - 88, "PHASE 2: FOUNDATION (Weeks 3-8)")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica", 10)
    phase2_tasks = [
        "Set up Skool community",
        "Create first 5-10 pieces of content",
        "Start YouTube channel",
        "Prepare Canada materials",
        "Maintain freelance clients"
    ]
    y = height - 115
    for task in phase2_tasks:
        c.drawString(width/2 + 37, y, f"• {task}")
        y -= 18

    # Phase 3 Box
    c.setFillColor(SURFACE)
    c.roundRect(36, height - 420, width - 72, 160, 8, fill=True, stroke=False)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(2)
    c.roundRect(36, height - 420, width - 72, 160, 8, fill=False, stroke=True)

    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 278, "PHASE 3: SCALE (Months 3-6)")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica", 10)
    phase3_tasks = [
        "Launch BJJ Intelligence publicly",
        "Deliver Canada speaking gig (March 2026)",
        "Scale to 50+ paying members",
        "Evaluate: Revisit AI Lunchbox?",
        "Evaluate: Revisit Jasen partnership?",
        "Target: $2-3K MRR from BJJ Intelligence"
    ]
    y = height - 305
    col1_x = 55
    col2_x = width/2 + 20
    for i, task in enumerate(phase3_tasks):
        x = col1_x if i < 3 else col2_x
        y_pos = y - (i % 3) * 18
        c.drawString(x, y_pos, f"• {task}")

    # Key Deadlines
    c.setFillColor(RELATIONSHIPS)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 460, "KEY DEADLINES")

    deadlines = [
        ("This Week", "Send Jasen decline message"),
        ("Week 2", "Freelance profiles live, start outreach"),
        ("Week 3", "BJJ Intelligence Skool setup complete"),
        ("Feb 7", "30th birthday - evaluate progress"),
        ("March", "Canada speaking gig"),
        ("Month 6", "Target: 50+ members, $2-3K MRR"),
    ]

    y = height - 485
    for when, what in deadlines:
        c.setFillColor(RELATIONSHIPS)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(55, y, when)
        c.setFillColor(TEXT_PRIMARY)
        c.setFont("Helvetica", 10)
        c.drawString(140, y, what)
        y -= 18

    # Footer
    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, 30, "Page 2 of 3 | Career Clarity Analysis - January 2026")

    c.showPage()

    # === PAGE 3: QUICK REFERENCE ===

    # Dark background
    c.setFillColor(BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Header
    c.setFillColor(ACCENT)
    c.rect(0, height - 50, width, 50, fill=True, stroke=False)

    c.setFillColor(BG)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - 35, "Quick Reference")

    # Decline Script Box
    c.setFillColor(SURFACE)
    c.roundRect(36, height - 280, width - 72, 210, 8, fill=True, stroke=False)
    c.setStrokeColor(DANGER)
    c.setLineWidth(2)
    c.roundRect(36, height - 280, width - 72, 210, 8, fill=False, stroke=True)

    c.setFillColor(DANGER)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 88, "DECLINE SCRIPT FOR JASEN")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica-Oblique", 10)
    script_lines = [
        '"Hey Jasen, I really appreciate the offer and our conversation.',
        'After doing deep analysis on my situation, I realized I need to',
        'focus on ONE thing right now instead of spreading across',
        'multiple communities.',
        '',
        'I\'ve got AI Foundations commitments plus something personal',
        'I want to build first.',
        '',
        'Can we revisit this in 3-6 months once I\'ve got more stability?',
        'I think we\'d be better partners then anyway."'
    ]
    y = height - 115
    for line in script_lines:
        c.drawString(55, y, line)
        y -= 15

    # Core Values Reminder
    c.setFillColor(SURFACE)
    c.roundRect(36, height - 430, width/2 - 54, 130, 8, fill=True, stroke=False)
    c.setStrokeColor(RELATIONSHIPS)
    c.setLineWidth(2)
    c.roundRect(36, height - 430, width/2 - 54, 130, 8, fill=False, stroke=True)

    c.setFillColor(RELATIONSHIPS)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 315, "CORE VALUES REMINDER")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica", 10)
    values = [
        '"It\'s a groovy thing to do"',
        "Creates for self first, market second",
        "BJJ still core identity",
        "Teaching is your gift"
    ]
    y = height - 340
    for val in values:
        c.drawString(55, y, f"• {val}")
        y -= 16

    # Decision Points
    c.setFillColor(SURFACE)
    c.roundRect(width/2 + 18, height - 430, width/2 - 54, 130, 8, fill=True, stroke=False)
    c.setStrokeColor(PLAY)
    c.setLineWidth(2)
    c.roundRect(width/2 + 18, height - 430, width/2 - 54, 130, 8, fill=False, stroke=True)

    c.setFillColor(PLAY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/2 + 32, height - 315, "DECISION POINTS")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica", 10)
    decisions = [
        "Revisit AI Lunchbox: Month 4-6",
        "Revisit Jasen: Q3 2026",
        "Pivot trigger: <20 members at Month 3",
        "Red flag: Runway depleted"
    ]
    y = height - 340
    for dec in decisions:
        c.drawString(width/2 + 37, y, f"• {dec}")
        y -= 16

    # Contact / Resources
    c.setFillColor(SURFACE)
    c.roundRect(36, height - 550, width - 72, 100, 8, fill=True, stroke=False)

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 465, "SUPPORTING DOCUMENTS")

    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica", 10)
    docs = [
        "Tony_Career_Clarity_Analysis_2026.md - Full analysis document",
        "Tony_Vision_Board_Evolution.xlsx - 2024 vs 2026 values comparison",
        "Tony_Skills_Inventory_2025-2026.xlsx - Complete skills inventory",
        "Tony_Opportunity_Matrix.xlsx - Scored decision matrix",
        "Jasen_Partnership_Analysis.xlsx - Partnership deep-dive"
    ]
    y = height - 490
    for doc in docs:
        c.drawString(55, y, f"• {doc}")
        y -= 14

    # Footer quote
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, 80, '"Follow the passion this time. The money follows')
    c.drawCentredString(width/2, 62, 'when you build something authentic."')

    # Page footer
    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, 30, "Page 3 of 3 | Career Clarity Analysis - January 2026")

    c.save()
    print("PDF created: D:/Projects/Project-Management/docs/Tony_Career_Clarity_Summary.pdf")

if __name__ == "__main__":
    create_executive_summary()
