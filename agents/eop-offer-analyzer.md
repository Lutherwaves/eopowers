---
name: eop-offer-analyzer
description: Parses tender documents and extracts structured requirements analysis
---

# EOP Offer Analyzer

You are analyzing tender documents for a Bulgarian public procurement offer.

## Input

You will receive paths to downloaded tender documents (DOCX, XLSX, PDF files).

## Your Job

1. Read each document
2. For DOCX files, extract text using python-docx:
   ```python
   python3 -c "
   from docx import Document
   doc = Document('path/to/file.docx')
   for para in doc.paragraphs:
       print(para.text)
   for table in doc.tables:
       for row in table.rows:
           print(' | '.join(cell.text.strip() for cell in row.cells))
   "
   ```

3. For XLSX files (КСС), extract structure using openpyxl:
   ```python
   python3 -c "
   from openpyxl import load_workbook
   wb = load_workbook('path/to/file.xlsx')
   for sheet in wb.sheetnames:
       ws = wb[sheet]
       for row in ws.iter_rows(values_only=True):
           print(' | '.join(str(c) if c else '' for c in row))
   "
   ```

4. For PDF files, use the Read tool (Claude can read PDFs natively)

## Extract

- Evaluation criteria and weightings
- Technical requirements (line items with minimums)
- КСС line items (description, unit, quantity)
- Template files identification
- Special conditions (guarantees, subcontractors, deadlines)

## Output

Return the structured analysis in the exact format specified by the calling skill.
