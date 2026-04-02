# environmental-disclosure-analysis

A Python-based text mining and data analysis project examining the
evolution of environmental disclosure language in corporate CSR
reports from 2002 to 2016.

## About
This project was completed as a group seminar assignment for the
Data Analysis and Visualisation course at Dalarna University (MSc
Data Science). It applies a rule-based keyword classification
framework to analyse whether corporate environmental reporting
became more substantive or symbolic over time, and whether GRI
framework transitions (G3 in 2006, G4 in 2013) improved
reporting accountability.

**Group 10:** Aikaterini Toumpa, Al Amin Alif,
Charitha Wickramasinghe, Tharindu Senanayake

## Research Questions
- How has the nature of environmental disclosure evolved from
  2002 to 2016 in terms of language and reporting quality?
- To what extent has the balance between symbolic and substantive
  disclosure shifted over time?
- Did GRI G3 (2006) and GRI G4 (2013) act as a catalyst in
  shifting industries toward substantive reporting?

## Key Findings
- Environmental reporting volume increased significantly between
  2002 and 2016, but substantive disclosure did not improve
- Symbolic language became more dominant over time — rising by
  9.4 percentage points by 2016
- GRI frameworks improved reporting structure and volume but
  did not increase accountability
- Corporate environmental reporting remains more
  communication-driven than performance-driven

## Methodology
- Rule-based text mining using four keyword dictionaries:
  Environmental Trigger Keywords, Type 1 Words (action),
  Type 2 Words (results), and Symbolic Words (intentions)
- Sentence-level classification into Substantive, Symbolic,
  Mixed, Neutral ENV, and Non-ENV categories
- Report-level scoring: environmental density, percentage
  shares per sentence type, TOTAL CLASS
- Longitudinal aggregation by year and GRI framework period
- Analysis covers 1,347 English-language CSR reports

## Project Structure
```
environmental-disclosure-analysis/
│
├── keywords_env.py        ← keyword dictionaries for classification
├── DAV_assignment.csv     ← processed results dataset
├── Group_10_Report_Sem2.pdf  ← full academic report
├── Group10_ppt_sem2.pptx  ← presentation slides
└── README.md
```

**Note:** The original raw dataset (txt files) is not included
due to file size. See setup instructions below.

## Setup Instructions
1. Locate the `Files/txt_files` folder in the project directory
2. Place all required `.txt` data files into that folder
3. The script reads directly from `Files/txt_files` and will
   not run without these files
4. Contact the repository owner to request the dataset if needed

## How to Run
```bash
python keywords_env.py
```

## Built With
- Python 3
- Rule-based NLP — keyword dictionaries and decision tree
  classification
- Text mining — sentence extraction and classification
- Data analysis — longitudinal aggregation and statistical
  comparison across GRI periods
- Data visualisation — time series and comparative charts

## Academic Context
Dalarna University · MSc Data Science
Course: Data Analysis and Visualisation
Seminar 2 Assignment · Group 10

## Dataset
CSR reports sourced from the GRI Database Corpus (2002–2016).
1,347 English-language reports analysed after filtering for
minimum quality thresholds.
