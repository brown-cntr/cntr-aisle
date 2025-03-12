import numpy as np
import pandas as pd
from datetime import datetime 

def convert_to_markdown(df):
    df = df.replace({'bill_type':{'Congress': 'Federal'}}) # wording
    
    df['bill_type'] = pd.Categorical(
        df['bill_type'],
        ['Model','Federal','State'],
        ordered=True
    )
    
    df = df.sort_values([
        'bill_type', 
        'bill_jurisdiction', 
        'bill_version_date'
    ]).reset_index(drop=True)
    
    df['enum_iter'] = (
        df
        .reset_index()
        .groupby('bill_type', observed=False)
        ['index'].rank()
        .astype('int')
    )
    
    df['bill_label'] = df.apply(
        lambda x: '{enum_iter}. **{bill_id}**: "*{bill_title}*" (Version: *{bill_version_date}*)'.format(**x),
        axis=1
    )
    
    text = '\n'.join(
        df.groupby('bill_type', observed=False)
        ['bill_label'].apply(lambda x: '\n'.join(x))
        .reset_index()
        .apply(
            lambda x: '## {bill_type} bills\n\n{bill_label}\n'.format(**x),
            axis=1
        )
    )
        
    return text

if __name__ == '__main__':
    INPUT_FILE = 'source/bill-metadata.csv'
    OUTPUT_FILE = 'docs/bills.md'
    VERSION = 'V1'
    
    df = pd.read_csv(INPUT_FILE)

    current_date = datetime.now().strftime('%B %d, %Y')
    
    text = f'''\
# CNTR AISLE Framework {VERSION}: **Bill list**

This is a list of bills that were assessed with the Center for Technological Responsibility's AI Legislation Evaluation Framework {VERSION} (**CNTR AISLE Framework**).

This is part of the **AI Legislative Mapping** project at the CNTR at Brown University.

Please contact us or raise an issue at <https://github.com/brown-cntr/cntr-aisle/> if you have questions or suggestions.

**Version**: *CNTR-AISLE-{VERSION}*

**Updated**: {current_date}

'''
    text += convert_to_markdown(df)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(text)