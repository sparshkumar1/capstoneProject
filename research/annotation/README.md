# Human Annotation Instructions & Data Package

This folder contains the standardized human evaluation artifacts for PREPAIred answer grading validation.

## Files
1. 
ater_guidelines.md: The complete scoring rubric, criteria definitions, and anti-keyword-stuffing rules.
2. 
ating_template.csv: Blank evaluation template with item identifiers, randomized prompts, candidate responses, and blinded scoring columns.
3. ../scripts/analyze_human_ratings.py: Script to compute inter-rater agreement (Krippendorff alpha, Spearman rho, Pearson r, MAE) across rater columns.

## Protocol for Replicating Multi-Rater Human Study
1. Recruit  \ge 3$ domain experts (Computer Science educators, senior software engineers, or teaching assistants).
2. Distribute 
ating_template.csv and 
ater_guidelines.md independently to each rater.
3. Instruct raters to complete scores in the score_0_to_1 column without consulting external tools or discussing with other raters.
4. Merge completed sheets into 
atings_completed.csv with columns 
ater_1, 
ater_2, ..., 
ater_K.
5. Run:
   `ash
   python research/scripts/analyze_human_ratings.py --input research/annotation/ratings_completed.csv
   `
