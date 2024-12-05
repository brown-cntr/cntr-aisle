import numpy as np
import pandas as pd
from datetime import datetime 

def convert_to_markdown(df):
    text = ''
    for row in df.to_dict('records'):
        term = row['Terms']
        defn = row['Definitions']
        ref = row['References']
        cat = row['Category']
        
        md_cat = ', '.join([
            f'*{x.strip()}*' for x in cat.split(',')
        ]) 
        
        text += (
            f'## {term}\n\n'
            f'**Definition**: {defn}\n\n'
            f'**Potential relevant categories**: {md_cat}\n\n'
        )

        text += (
            '' if pd.isna(ref) else
            f'**Reference**: {ref}\n'
        )

        text += '\n'
        
    return text

if __name__ == '__main__':
    INPUT_FILE = 'source/definitions.csv'
    OUTPUT_FILE = 'docs/index.md'
    
    df = pd.read_csv(INPUT_FILE)    
    assert all(df['Deprecated'].isin([None, np.nan, "No"]))


    current_date = datetime.now().strftime('%B %d, %Y')
    
    text = f'''\
# AI / ADS Scorecard Term Definitions

This document provides the definitions of the terms used in questions of the Scorecard for Artificial Intelligence (AI) and Automated Decision Systems (ADS) Policy.

This is part of the AI Legislative Mapping project at the CNTR at Brown University. 

Please contact us or raise an issue at <https://github.com/brown-cntr/scorecard-definitions/> if you have questions or suggestions.

**Updated**: {current_date}

'''
    text += convert_to_markdown(df)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(text)