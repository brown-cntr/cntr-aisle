import re
import numpy as np
import pandas as pd
from datetime import datetime 

# additional info needed to render
multi_choice_opts = {
    'G1a': [
        'OECD: An AI system is a machine-based system that, for explicit or implicit objectives, infers, from the input it receives, how to generate outputs such as predictions, content, recommendations, or decisions that can influence physical or virtual environments. Different AI systems vary in their levels of autonomy and adaptiveness after deployment.',
        '2019 NDAA: (1) Any artificial system that performs tasks under varying and unpredictable circumstances without significant human oversight, or that can learn from experience and improve performance when exposed to data sets. (2) An artificial system developed in computer software, physical hardware, or other context that solves tasks requiring human-like perception, cognition, planning, learning, communication, or physical action. (3) An artificial system designed to think or act like a human, including cognitive architectures and neural networks. (4) A set of techniques, including machine learning, that is designed to approximate a cognitive task. (5) An artificial system designed to act rationally, including an intelligent software agent or embodied robot that achieves goals using perception, planning, reasoning, learning, communicating, decision making, and acting.',
        '2020 NDAA: The term ‘‘artificial intelligence’’ means a machine-based system that can, for a given set of human-defined objectives, make predictions, recommendations or decisions influencing real or virtual environments. Artificial intelligence systems use machine and human-based inputs to— (A) perceive real and virtual environments; (B) abstract such perceptions into models through analysis in an automated manner; and (C) use model inference to formulate options for information or action.',
        'EU AI Act: "AI system" means a machine-based system that is designed to operate with varying levels of autonomy and that may exhibit adaptiveness after deployment, and that, for explicit or implicit objectives, infers, from the input it receives, how to generate outputs such as predictions, content, recommendations, or decisions that can influence physical or virtual environments;',
        'EU AI Act: "General-purpose AI model" means an AI model, including where such an AI model is trained with a large amount of data using self-supervision at scale, that displays significant generality and is capable of competently performing a wide range of distinct tasks regardless of the way the model is placed on the market and that can be integrated into a variety of downstream systems or applications, except AI models that are used for research, development or prototyping activities before they are placed on the market;',
        'N/A',
    ],
    'G1b': [
        'General v1: "Automated decision system" means a computational process, including one derived from machine learning, statistics, or other data processing or artificial intelligence techniques, that makes a decision, or facilitates human decision making  [usually followed by potential impacted entities]... [Example sources: US S-2134 (117th); SC S-404 (2023-2024)]',
        'General v2: "Automated decision system" means any computer program, method, statistical model, or process that aims to aid or replace human decision-making using algorithms or artificial intelligence. [Example source: RI SB-146 (2023)]',
        'Definition with "threshold" on decision: “Automated decision tool” means a system or service that uses artificial intelligence and has been specifically developed and marketed to, or specifically modified to, make, or be a controlling factor in making, consequential decisions. [Example source: CA AB-331 (2023-2024)]',
        'Government purpose v1: The term "automated decision system" means a system, software, or process that (i) uses computation, in whole or in part, to determine outcomes, make or aid decisions (including through evaluations, metrics, or scoring), inform policy implementation, collect data or observations, or otherwise interact with individuals or communities, including such a system, software, or process derived from machine learning, statistics, or other data processing or artificial intelligence techniques; and (ii) is not passive computing infrastructure. [Example source: US S-262 (118th)]',
        'Government purpose v2: "Automated decision system" means any machine-based system or application, including, but not limited to, any such system or application that is derived from machine learning, statistics, or other data processing or artificial intelligence techniques, which system is developed, procured, or utilized to make, inform, or materially support a critical decision made by a State agency. "Automated decision system" does not include passive computing infrastructure. [Example source: NJ S-1438 (221st)]',
        'Government purpose v3: "Automated decision system" means an algorithm, including an algorithm incorporating machine learning or other artificial intelligence techniques, that uses data-based analytics to make or support governmental decisions, judgments, or conclusions. [Example source: ID H-568 (2024)]',
        'N/A',
    ],
    'G1bi': [
        'Yes',
        'No',
        'N/A'
    ],
}

additional_notes = {
    'Accountability & Transparency': 'Note: In this category of Accountability & Transparency, “IA” will refer to Impact Assessment and “RA” to Risk Assessment throughout this scorecard. Both terms will be treated synonymously within this category.',
}

def convert_to_markdown(df):
    # fix typo
    df.loc[
        df['question_code'] == "G1b",
        'source_question_col'
    ] = df.loc[df['question_code'] == "G1b", 'question'].str.replace(
        'please please',
        'please'
    )
    
    # sort the order of questions based on index
    df = df.reset_index()
    df = df.merge(
        df.groupby(['category','category_section'])
        ['index'].mean().rank()
        .to_frame('category_section_rank')
        .astype('int')
        .reset_index()
    ).merge(
        df.groupby(['category'])
        ['index'].mean().rank()
        .to_frame('category_rank')
        .astype('int')
        .reset_index()
    )
    
    # display format
    df['display_question'] = df.apply(
        lambda x: (
            x['question'] if x['source_question_col'].startswith(x['category_section'])
            else x['source_question_col']
        ),
        axis=1
    )
    
    df['display_question'] = df.apply(
        lambda x: (
            x['question_code'] + ': ' + x['display_question'] 
            if x['question_code'] not in multi_choice_opts
            else x['display_question'] + '\n\n' + '\n'.join([
                '- *' + c + '*' for c in multi_choice_opts[x['question_code']]
            ])
        ),
        axis=1
    )
    
    ques_disp_df = (
        df
        .reset_index()
        .groupby([
            'category', 'category_code', 
            'category_rank',  
            'category_section',
            'category_section_rank'
        ])
        ['display_question'].agg(list)
        .apply(lambda x: '\n\n'.join(x))
        .reset_index()
        .sort_values([
            'category_rank',
            'category_section_rank'
        ])
    )
    
    ques_disp_df['display_section'] = ques_disp_df.apply(
        lambda x: '### {category_section}\n\n{display_question}\n\n'.format(**x),
        axis=1
    )
    
    ques_disp_df = (
        ques_disp_df
        .groupby([
            'category',
            'category_code',
            'category_rank',
        ])
        ['display_section'].agg(list)
        .apply(lambda x: '\n\n'.join(x))
        .reset_index()
    )
    
    ques_disp_df['pre_notes'] = (
        ques_disp_df['category'].map(additional_notes)
        .apply(lambda x: '*' + x + '*' if not pd.isna(x) else '')
    )
    
    ques_disp_df['category'] = ques_disp_df['category'].str.upper()
    
    ques_disp_df['category_label'] = (
        ques_disp_df['category'].str.upper() + 
        ' (*' + ques_disp_df['category_code'].str.upper() + '*)\n\n'
        + ques_disp_df['pre_notes']
    )
    
    text = '\n'.join(
        ques_disp_df.sort_values('category_rank')
        .apply(
            lambda x: '## {category} ({category_code})\n\n{pre_notes}\n\n{display_section}\n'.format(**x),
            axis=1
        )
    )
    
    text = re.sub(
        r'(\b' + '|'.join(df['question_code']) + r'\b):',
        r'[**\1**]',
        text
    )


    return text

if __name__ == '__main__':
    INPUT_FILE = 'source/question-metadata.csv'
    OUTPUT_FILE = 'docs/framework.md'
    VERSION = 'V1'
    
    df = pd.read_csv(INPUT_FILE)

    current_date = datetime.now().strftime('%B %d, %Y')
    
    text = f'''\
# CNTR AISLE Framework {VERSION}: **Questions**

The following are the questions of the Center for Technological Responsibility's AI Legislation Evaluation Framework {VERSION} (**CNTR AISLE Framework**).

This is part of the **AI Legislative Mapping** project at the CNTR at Brown University.

Please contact us or raise an issue at <https://github.com/brown-cntr/cntr-aisle/> if you have questions or suggestions.

**Version**: *CNTR-AISLE-{VERSION}*

**Updated**: {current_date}

'''
    text += convert_to_markdown(df)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(text)