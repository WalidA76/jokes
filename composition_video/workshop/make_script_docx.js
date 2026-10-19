const fs = require('fs');
const D = require('docx');
const C = require('./script_content.js');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType, HeadingLevel, LevelFormat, Footer, PageNumber, TabStopType } = D;

const FONT = 'Tajawal Medium', COPPER = 'B8651B', INK = '1A1A1A', GREY = '666666';
const bidi = (o = {}) => ({ bidirectional: true, ...o });
const run = (t, o = {}) => { const { italics, ...r } = o; return new TextRun({ text: t, font: r.bold ? 'Tajawal' : 'Tajawal Medium', rightToLeft: true, ...r }); };

const P = (t, o = {}, r = {}) => new Paragraph(bidi({ spacing: { after: 140, line: 360 }, children: [run(t, r)], ...o }));
const boxed = (t, fill, color, bold = false) => new Paragraph(bidi({
  spacing: { before: 60, after: 140, line: 320 },
  shading: { type: ShadingType.CLEAR, fill, color: 'auto' },
  border: { right: { style: BorderStyle.SINGLE, size: 24, color, space: 8 } },
  indent: { left: 120, right: 120 },
  children: [run(t, { size: 24, bold, color: INK })],
}));

const cellB = { style: BorderStyle.SINGLE, size: 4, color: 'D9D9D9' };
const borders = { top: cellB, bottom: cellB, left: cellB, right: cellB };
function cell(t, w, o = {}) {
  return new TableCell({ width: { size: w, type: WidthType.DXA }, borders, margins: { top: 80, bottom: 80, left: 120, right: 120 },
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
    children: [new Paragraph(bidi({ children: [run(t, { size: 22, bold: !!o.bold, color: o.color || INK })] }))] });
}
function table(widths, head, rows) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, visuallyRightToLeft: true,
    rows: [new TableRow({ tableHeader: true, children: head.map((h, i) => cell(h, widths[i], { fill: '1F1F22', bold: true, color: 'FFFFFF' })) }),
      ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, widths[i])) }))] });
}

const kids = [];
kids.push(new Paragraph(bidi({ spacing: { before: 400, after: 120 }, children: [run(C.title, { size: 52, bold: true, color: INK })] })));
kids.push(new Paragraph(bidi({ spacing: { after: 320 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COPPER, space: 6 } }, children: [run(C.subtitle, { size: 30, color: COPPER, bold: true })] })));
kids.push(P('هذا السكربت مبني على «دليل ورشة أساسيات التصوير الفوتوغرافي». كل محور يحتوي على: نص التسجيل بالترتيب، وإشارات ظهور الجرافيك (ملف منفصل لكل محور بمقاس 16:9)، وتوجيهات الأداء الميداني أمام الكاميرا. النص مكتوب بلغة بيضاء قريبة من الحديث، فعدّله بما يناسب لهجتك وأمثلتك.', {}, { size: 24 }));

kids.push(new Paragraph(bidi({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: [run('رموز السكربت', { size: 30, bold: true, color: COPPER })] })));
kids.push(table([2600, 6800], ['الرمز', 'المعنى'], C.legend));
kids.push(new Paragraph(bidi({ heading: HeadingLevel.HEADING_2, spacing: { before: 320, after: 120 }, children: [run('جدول التوقيت والجرافيك', { size: 30, bold: true, color: COPPER })] })));
kids.push(table([4600, 1500, 3300], ['الفقرة', 'المدة', 'ملف الجرافيك'], C.timing));
kids.push(P('المجموع التقريبي: 48 دقيقة (40 دقيقة محاور + افتتاح وخلاصة ومشروع التخرج).', { spacing: { before: 120, after: 120 } }, { size: 22, color: GREY }));

C.sections.forEach((s, i) => {
  kids.push(new Paragraph(bidi({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, spacing: { after: 80 }, children: [run(s.h1, { size: 38, bold: true, color: INK })] })));
  kids.push(new Paragraph(bidi({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COPPER, space: 6 } },
    children: [run('المدة المقترحة: ' + s.dur, { size: 24, color: COPPER, bold: true }), ...(s.graphic ? [run('     |     الجرافيك: ' + s.graphic, { size: 22, color: GREY })] : [])] })));
  s.blocks.forEach(([k, v]) => {
    if (k === 'h2') kids.push(new Paragraph(bidi({ keepNext: true, spacing: { before: 220, after: 100 }, children: [run(v, { size: 30, bold: true, color: COPPER })] })));
    else if (k === 'say') kids.push(P(v, {}, { size: 28 }));
    else if (k === 'cue') kids.push(boxed(v, 'FFF1E3', 'E8873A', true));
    else if (k === 'direct') kids.push(boxed(v, 'E6F3F6', '2FA8B8'));
    else if (k === 'tip') kids.push(new Paragraph(bidi({ spacing: { after: 120 }, children: [run(v, { size: 22, italics: true, color: GREY })] })));
    else if (k === 'bullets') v.forEach(b => kids.push(new Paragraph(bidi({ numbering: { reference: 'bul', level: 0 }, spacing: { after: 100, line: 340 }, children: [run(b, { size: 26 })] }))));
  });
});

const doc = new Document({
  creator: 'Walidphotoz', title: C.title,
  styles: { default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 38, bold: true, font: FONT }, paragraph: { outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 30, bold: true, font: FONT }, paragraph: { outlineLevel: 1 } }] },
  numbering: { config: [{ reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1000, bottom: 1000, left: 1000, right: 1000 } }, bidi: true },
    footers: { default: new Footer({ children: [new Paragraph(bidi({ alignment: AlignmentType.CENTER, children: [run('سكربت ورشة أساسيات التصوير — صفحة ', { size: 18, color: GREY }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: GREY })] }))] }) },
    children: kids,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync('workshop_recording_script.docx', b); console.log('ok'); });
