"""WealthNest invoice PDF generator using ReportLab."""
import io
import re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

# Brand colors
INDIGO = colors.HexColor('#1E1B4B')
GOLD = colors.HexColor('#F6C90E')
GREEN = colors.HexColor('#10B981')
CORAL = colors.HexColor('#FF6B6B')
TEXT_MUTED = colors.HexColor('#6B7280')
SURFACE = colors.HexColor('#FFF8DC')
BORDER = colors.HexColor('#ECE9E0')


def _strip_emoji(text):
    """ReportLab's default fonts don't ship with emoji glyphs — strip them."""
    if not text:
        return ''
    # Remove most emoji ranges + variation selectors
    return re.sub(
        r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\uFE0F]',
        '',
        text,
    ).strip()


def generate_invoice_pdf(payment):
    """Build and return a BytesIO PDF for the given Payment."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=f'Invoice {payment.invoice_number}',
        author='WealthNest',
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='BrandTitle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=22, textColor=INDIGO,
        leading=26, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='Tagline', parent=styles['Normal'],
        fontSize=8, textColor=TEXT_MUTED, leading=10,
    ))
    styles.add(ParagraphStyle(
        name='RightLabel', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, textColor=INDIGO,
        alignment=TA_RIGHT, leading=22,
    ))
    styles.add(ParagraphStyle(
        name='RightSmall', parent=styles['Normal'],
        fontSize=9, textColor=TEXT_MUTED, alignment=TA_RIGHT,
    ))
    styles.add(ParagraphStyle(
        name='SectionLabel', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, textColor=TEXT_MUTED,
        leading=10,
    ))
    styles.add(ParagraphStyle(
        name='Field', parent=styles['Normal'],
        fontSize=10, textColor=INDIGO, leading=14,
    ))
    styles.add(ParagraphStyle(
        name='FieldBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, textColor=INDIGO, leading=14,
    ))
    styles.add(ParagraphStyle(
        name='Note', parent=styles['Normal'],
        fontSize=9, textColor=TEXT_MUTED, leading=12, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name='DemoNote', parent=styles['Normal'],
        fontSize=9, textColor=INDIGO, leading=12,
        backColor=SURFACE, borderPadding=8, borderColor=GOLD, borderWidth=0,
    ))

    story = []

    # ===== Header =====
    header_data = [[
        [
            Paragraph('Wealth<font color="#F6C90E">Nest</font>', styles['BrandTitle']),
            Paragraph('Family Financial Literacy Platform', styles['Tagline']),
            Paragraph('noreply@wealthnest.app · BCA Project Demo', styles['Tagline']),
        ],
        [
            Paragraph('INVOICE', styles['RightLabel']),
            Paragraph(f'<b>{payment.invoice_number}</b>',
                      ParagraphStyle(name='InvNum', parent=styles['Normal'],
                                     fontSize=10, textColor=INDIGO, alignment=TA_RIGHT)),
            Paragraph(payment.created_at.strftime('%d %b %Y · %H:%M'), styles['RightSmall']),
        ],
    ]]
    header = Table(header_data, colWidths=[100 * mm, 70 * mm])
    header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -1), 2, GOLD),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(header)
    story.append(Spacer(1, 10))

    # ===== Billed To / Status =====
    billed_to_data = [[
        [
            Paragraph('BILLED TO', styles['SectionLabel']),
            Paragraph(_strip_emoji(payment.payer_name) or '—', styles['FieldBold']),
            Paragraph(_strip_emoji(payment.subscription.family.family_name), styles['Field']),
            Paragraph(f'Family ID: #{payment.subscription.family.family_id}', styles['Field']),
        ],
        [
            Paragraph('STATUS', styles['SectionLabel']),
            _status_badge(payment.status),
            Paragraph(f'<b>Txn:</b> {payment.transaction_id}', styles['Field']),
        ],
    ]]
    billed = Table(billed_to_data, colWidths=[100 * mm, 70 * mm])
    billed.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(billed)
    story.append(Spacer(1, 16))

    # ===== Line items =====
    plan_label = f'WealthNest {_strip_emoji(payment.plan.name)} Plan'
    line_items = [
        ['Description', 'Cycle', 'Amount'],
        [
            [
                Paragraph(f'<b>{plan_label}</b>', styles['Field']),
                Paragraph(_strip_emoji(payment.plan.tagline), styles['Tagline']),
            ],
            payment.billing_cycle.capitalize(),
            f'INR {payment.amount:,.2f}',
        ],
    ]
    items_table = Table(line_items, colWidths=[100 * mm, 30 * mm, 40 * mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SURFACE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), INDIGO),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, GOLD),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('FONTNAME', (2, 1), (2, 1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (2, 1), (2, 1), INDIGO),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, BORDER),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # ===== Totals =====
    totals_data = [
        ['Subtotal', f'INR {payment.amount:,.2f}'],
        ['GST (Demo)', 'INR 0.00'],
        ['TOTAL PAID', f'INR {payment.amount:,.2f}'],
    ]
    totals = Table(totals_data, colWidths=[40 * mm, 40 * mm], hAlign='RIGHT')
    totals.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('TEXTCOLOR', (0, 0), (-1, -2), TEXT_MUTED),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 13),
        ('TEXTCOLOR', (0, -1), (0, -1), INDIGO),
        ('TEXTCOLOR', (1, -1), (1, -1), GREEN),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(totals)
    story.append(Spacer(1, 16))

    # ===== Payment details =====
    method_lines = [
        ['Method', payment.get_payment_method_display()],
    ]
    if payment.last_four:
        method_lines.append(['Card', f'**** **** **** {payment.last_four}'])
    if payment.upi_id:
        method_lines.append(['UPI ID', payment.upi_id])
    if payment.bank_name:
        method_lines.append(['Bank', payment.bank_name])
    method_lines.append(['Currency', payment.currency])
    if payment.subscription.expires_at:
        method_lines.append([
            'Subscription expires',
            payment.subscription.expires_at.strftime('%d %b %Y'),
        ])

    pd_table = Table(
        [[Paragraph('PAYMENT DETAILS', styles['SectionLabel']), '']] + method_lines,
        colWidths=[50 * mm, 120 * mm],
    )
    pd_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('TEXTCOLOR', (0, 1), (0, -1), TEXT_MUTED),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1, 1), (1, -1), INDIGO),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(pd_table)
    story.append(Spacer(1, 16))

    # Demo notice
    demo_note = Table(
        [[Paragraph(
            f'<b>Demo Notice:</b> {_strip_emoji(payment.notes) or "This is a simulated payment for the BCA project demo. No real money was transferred."}',
            styles['Field'],
        )]],
        colWidths=[170 * mm],
    )
    demo_note.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SURFACE),
        ('LINEBEFORE', (0, 0), (0, -1), 4, GOLD),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(demo_note)
    story.append(Spacer(1, 18))

    story.append(Paragraph(
        'Thank you for being part of WealthNest!<br/>'
        'Generated on ' + datetime.now().strftime('%d %b %Y, %H:%M'),
        styles['Note'],
    ))

    doc.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    buf.seek(0)
    return buf


def _status_badge(status):
    """Return a coloured badge paragraph for the payment status."""
    color_map = {
        'success': GREEN,
        'failed': CORAL,
        'pending': GOLD,
        'refunded': TEXT_MUTED,
    }
    bg = color_map.get(status, INDIGO)
    return Paragraph(
        f'<para alignment="left"><font backColor="{bg.hexval()}" '
        f'color="white"><b>&nbsp; {status.upper()} &nbsp;</b></font></para>',
        ParagraphStyle(name='Badge', fontSize=11, leading=14),
    )


def _draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(
        18 * mm, 10 * mm,
        'WealthNest · BCA Final Year Project · Demo invoice — no real funds transferred.',
    )
    canvas.drawRightString(
        A4[0] - 18 * mm, 10 * mm,
        f'Page {doc.page}',
    )
    canvas.restoreState()
