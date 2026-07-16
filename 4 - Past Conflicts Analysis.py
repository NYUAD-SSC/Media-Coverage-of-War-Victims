#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%% Overview

"""
The code below generates the following list of supplementary figures:
    
    Supplementary Figures
    
    Supp Fig 12: Ratio of individualized to grouped mentions per side for each 
                 media source across the four wars.
    
    
    
    Supp Fig 13: Actual casualty counts and individualized casualty-related 
                 story percentages per side for each media source.
    
    
    
    Supp Fig 14: Figure shows the overall share of CVN statements that had 
                 Casting Doubt phrases in terms of Source Doubting and 
                 Uncertainty in Numbers.
    
"""


#%% Libraries

import pandas as pd
import numpy as np


#%% Paths

# Response Data

path_response_IG_prompt_1_past  = "03- LLM Response Data/Response Data - Individualized-Grouped - P1 - Find Hardship Instances - Past Conflicts.csv"

path_response_IG_prompt_2_past  = "03- LLM Response Data/Response Data - Individualized-Grouped - P2 - Label Hardship Instances - Past Conflicts.csv"

path_response_CVN_prompt_1_past = "03- LLM Response Data/Response Data - CVN Instances - Past Conflicts_1.csv"
path_response_CVN_prompt_1_past = "03- LLM Response Data/Response Data - CVN Instances - Past Conflicts.csv"

path_response_CVN_prompt_1_2023 = '03- LLM Response Data/Response Data - CVN Instances.csv'


# Aggregated Data

path_past_conflict_agg_data    = "04- Past Conflict Aggregated Data/"


# Secondary Data
path_plot_colors               = "02- Secondary Data/02- Project Plotting Colors.xlsx"

path_critical_events           = '02- Secondary Data/03- Conflict Events.xlsx'

path_report                    = '05- Report Plots and Tables/'

cd_phrases_path                = '02- Secondary Data/05- CVN - Casting Doubt - Critical Phrases.xlsx'




# %% Dictionaries

dict_colors  = pd.read_excel(path_plot_colors, usecols = ["Entity","Color"])

dict_colors  = dict_colors.dropna().set_index('Entity')['Color'].to_dict()

dict_sources = { "Al Jazeera English":"AJE", 
                "BBC":"BBC",
                "CNN Wire": "CNN", 
                "The New York Times":"NYT" }
     
sorted_sources = list(dict_sources.values())

sorted_sources.sort()




# %% Supp Fig 12

print("\nGenerating Supp Fig 12")

#%%% Import and Clean Data


# Read IG Prompt 1 Response Output
df_prompt_1_raw = pd.read_csv(path_response_IG_prompt_1_past)

df_prompt_1_raw = df_prompt_1_raw[df_prompt_1_raw['Type']!='Error'].copy()



#%%% Generate Data

# Generate Instance - Count Tables and Regression Reports for all 3 Conflicts

IG_1_Ratios = []


for conflict_year in [2008, 2012, 2014]:
    
    print("\nProcessing Conflict Data {}...".format(conflict_year))
    
    df_prompt_1 = df_prompt_1_raw[df_prompt_1_raw['Conflict_Year'] == conflict_year].copy()


    ### Clean Data - Indiv

    # Initial Filtering

    # -  keep only individualized instances
    df_indiv = df_prompt_1[df_prompt_1['Type']=="Individualized"].copy()


    # -  filter side = Pal / Isr 

    filter_side = df_indiv['Side'].isin(['Palestine','Israel'])

    df_indiv = df_indiv[filter_side].copy()


    # -  keep only Primary/Secondary entities

    df_indiv_prim = df_indiv[df_indiv['Primary']=="Yes"].copy()

    df_indiv_sec = df_indiv[df_indiv['Primary']=="No"].copy()



    # -  remove duplicate entities
    df_indiv_prim = df_indiv_prim.groupby(['Article_ID','Entity', 'Side','Civilian_Status', 
                       'Date', 'Source', 'Location'])['Phrases'].apply(set).reset_index()


    # Secondary Filtering (to be applied to any prompt after prompt 1 to match filtering)

    # -  double check - remove duplicate entities
    df_indiv_prim = df_indiv_prim.drop_duplicates(['Article_ID','Entity','Side'])

    df_indiv_sec  = df_indiv_sec.drop_duplicates(['Article_ID','Entity','Side'])


    # - keep Civilian entities
    df_indiv_prim['Civilian_Status'] = df_indiv_prim['Civilian_Status'].apply(lambda x: "Non-Civilian" if (x=="Military") | (x=="Government") else x)

    df_indiv_prim = df_indiv_prim[df_indiv_prim['Civilian_Status']=='Civilian'].copy()


    df_indiv_sec['Civilian_Status'] = df_indiv_sec['Civilian_Status'].apply(lambda x: "Non-Civilian" if (x=="Military") | (x=="Government") else x)

    df_indiv_sec = df_indiv_sec[df_indiv_sec['Civilian_Status']=='Civilian'].copy()


    # -  filter location - Gaza/Israel
    df_indiv_prim = df_indiv_prim[df_indiv_prim['Location'].str.contains('Gaza|Israel', case=False)].copy()

    df_indiv_sec = df_indiv_sec[df_indiv_sec['Location'].str.contains('Gaza|Israel', case=False)].copy()


    # -  generate counts for primary/secondary per side
    df_indiv_prim['Side'].value_counts().reset_index()

    df_indiv_sec['Side'].value_counts().reset_index()


    # -  take the indiv instances to be the primary ones only
    df_indiv = df_indiv_prim.copy()



    ### Clean Data - Group

    # Initial Filtering

    # -  keep only individualized instances
    df_group = df_prompt_1[df_prompt_1['Type']=="Grouped"].copy()



    # -  filter side = Pal / Isr 
    df_group = df_group[df_group['Side'].isin(['Palestine','Israel'])].copy()


    # -  keep only the non-Quoted entities
    df_group = df_group[df_group['Quoted']!="Yes"].copy()



    # Secondary Filtering

    # - keep Civilian entities
    df_group['Civilian_Status'] = df_group['Civilian_Status'].apply(lambda x: "Non-Civilian" if (x=="Military") | (x=="Government") else x)

    df_group = df_group[df_group['Civilian_Status']=='Civilian'].copy()


    # -  filter location - Gaza/Israel
    df_group = df_group[df_group['Location'].str.contains('Gaza|Israel', case=False)].copy()



    # %%% Calculate Indiv-Grouped Ratios


    # Table 1: Individualized - Grouped Instance Count Ratios
    count_ind = df_indiv.groupby(['Source','Side'])['Article_ID'].count()


    count_grp = df_group.groupby(['Source','Side'])['Article_ID'].count()


    count_ind_grp = count_ind.reset_index().merge(count_grp.reset_index(), on = ['Source','Side'])

    count_ind_grp = count_ind_grp.rename(columns={'Article_ID_x':'Indiv_Counts',
                                                  'Article_ID_y': 'Group_Counts'})



    df_table_1 = ((count_ind/count_grp)).round(2).reset_index().sort_values(['Source','Side'],ascending=[True, False]).reset_index(drop=True)

    df_table_1 = df_table_1.rename(columns={'Article_ID':'Indiv_to_Group_Ratio'})

    df_table_1 = count_ind_grp.merge(df_table_1, on = ['Source','Side'])

    a_T1_IG_Ratios = df_table_1.sort_values(['Source','Side'], ascending = [True, False])
    
    
    # Modification for the Past Conflicts Dataset
    a_T1_IG_Ratios['Year'] = conflict_year
    
    
    # Store Tables for documentation purposes
    title_i = "IG_Prompt_1_Instance_Counts_Ratios_Conflict_{}.csv".format(str(conflict_year))
    
    a_T1_IG_Ratios.to_csv(path_past_conflict_agg_data+title_i)

    IG_1_Ratios.append(a_T1_IG_Ratios)

  

    #%%% Plot Figure
    
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Read the IG Counts+Ratios
a_T1_IG_Ratios_08, a_T1_IG_Ratios_12, a_T1_IG_Ratios_14 = IG_1_Ratios

a_T1_IG_Ratios_23 = pd.read_csv(path_past_conflict_agg_data + "IG_Prompt_1_Instance_Counts_Ratios_Conflict_2023.csv")

# Create the 2008-2012 dataset - Merge the 2008 and 2012 data
a_T1_IG_Ratios_08_12 = a_T1_IG_Ratios_08.copy()
a_T1_IG_Ratios_08_12['Indiv_Counts'] = a_T1_IG_Ratios_08['Indiv_Counts'] + a_T1_IG_Ratios_12['Indiv_Counts']
a_T1_IG_Ratios_08_12['Group_Counts'] = a_T1_IG_Ratios_08['Group_Counts'] + a_T1_IG_Ratios_12['Group_Counts']

a_T1_IG_Ratios_08_12['Indiv_to_Group_Ratio'] = np.round(a_T1_IG_Ratios_08_12['Indiv_Counts']/a_T1_IG_Ratios_08_12['Group_Counts'],2)
a_T1_IG_Ratios_08_12['Year'] = '2008-2012'

plot_font = 25
sns.set_theme(style="white")

# 1. Create a single figure with 3 rows and 1 column. 
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(25, 24), dpi=600, sharex=True)

years = ['2008-2012', '2014', '2023']

data_list = [a_T1_IG_Ratios_08_12, a_T1_IG_Ratios_14, a_T1_IG_Ratios_23]

# 2. Iterate through the subplots simultaneously
for conflict_year, a_T1_IG_Ratios, ax in zip(years, data_list, axes):

    # Create the plot on the specific 'ax'
    ig_p1_barplot = sns.barplot(
        data=a_T1_IG_Ratios, 
        x="Indiv_to_Group_Ratio", 
        y="Source", 
        hue="Side", 
        palette=dict_colors, 
        ax=ax
    )
    
    # Add a number next to each horizontal bar (Palestine and Israel)
    ig_p1_barplot.bar_label(ax.containers[0], fontsize=plot_font-5, fontweight='bold', padding=5)
    ig_p1_barplot.bar_label(ax.containers[1], fontsize=plot_font-5, fontweight='bold', padding=5)

    # Replace the title with the year as the y-axis label
    ax.set_ylabel(conflict_year, fontsize=plot_font + 5, fontweight='bold', labelpad=20)
        
    # Control y-axis ticks (keeps your sources hidden/tiny as in your original setup)
    ax.tick_params(axis='y', labelsize=1)
    
    # Control x-axis scale and ticks
    ticks = np.arange(0, 0.36, 0.05)   
    ax.set_xticks(ticks)
    ax.set_xlim(0, 0.35)
    
    # Adjust the legend - remove side legend on each subplot so we can make a master legend
    ax.get_legend().remove()
    
    # Remove top and right borders
    sns.despine(ax=ax)

# 3. Set the x-axis label ONLY on the bottom subplot (axes[-1])
axes[-1].set_xlabel('Individual Stories to Group Mentions Ratios', 
                    fontweight='bold', 
                    labelpad=30, 
                    fontsize=plot_font + 12)
axes[-1].tick_params(axis='x', labelsize=plot_font)

# 4. Add a single unified legend for the whole figure at the top, centered, 2 columns
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, 
           loc='lower center',          # Anchors the bottom of the legend box
           bbox_to_anchor=(0.5, 1.01),  # Places it right above the top center of the subplots
           ncol=2,                      # 1 line, 2 columns
           fontsize=plot_font, 
           frameon=False)               # Optional: removes the box around the legend for a cleaner look

# Adjust layout so labels don't get cut off
plt.tight_layout()

# 5. Save the combined figure
title_i = 'Supp Fig 12 - Ratio of individualized to grouped mentions per side for each media source across the four wars.svg'
plt.savefig(path_report + title_i, format='svg', bbox_inches='tight')

    

#%% Supp Fig 13

print("\nGenerating Supp Fig 13")

#%%% Generate Data

# Import Cleaned Hardship Label Response Data

df_hard_emp = pd.read_csv(path_response_IG_prompt_2_past)


# Clean Prompt 2 & Empathy

# -  convert date col to datetime
#df_hard_emp['Date'] = pd.to_datetime(df_hard_emp['Date'], format = "%Y-%m-%d")
df_hard_emp['Date'] = pd.to_datetime(df_hard_emp['Date'], format = "%d %B %Y")


# -  double check - remove duplicate entities
df_hard_emp = df_hard_emp.drop_duplicates(['Article_ID','Entity','Side'])


# - keep Civilian entities
df_hard_emp['Civilian_Status'] = df_hard_emp['Civilian_Status'].apply(lambda x: "Non-Civilian" if (x=="Military") | (x=="Government") else x)

df_hard_emp = df_hard_emp[df_hard_emp['Civilian_Status']=='Civilian'].copy()


# -  filter location - Gaza/Israel
df_hard_emp = df_hard_emp[df_hard_emp['Location'].str.contains('Gaza|Israel', case=False)].copy()


tables_p2 = []

for conflict_year in [2008, 2012, 2014]:

    # import the relevant columns only of the merged data

    df_prompt_2 = df_hard_emp[df_hard_emp['Conflict_Year']==conflict_year].copy()


    # Count Hardship Sublabels


    # Get count of hardship per side per source

    #df_hardship_simple = df_prompt_2.groupby(['Source','Side', 'Hardship'])['Instance_ID'].count().reset_index().sort_values(['Source','Side','Instance_ID'],ascending=[True, False, False])
    df_hardship_simple = df_prompt_2.groupby(['Source','Side', 'Hardship'])['Instance_ID'].count().reset_index().sort_values(['Source','Side','Instance_ID'],ascending=[True, False, False])

    df_hardship_simple = df_hardship_simple.rename(columns = {'Instance_ID':'Instance_Count'})

    df_hardship = df_hardship_simple.pivot(index = ['Source', 'Side'], columns='Hardship', values='Instance_Count').fillna(0)

    df_hardship = df_hardship.reset_index().sort_values(['Source','Side'],ascending=[True, False]).reset_index(drop=True).set_index(['Source','Side'])

    df_hardship['Total'] = df_hardship.sum(axis=1)


    # Calculate the Pal to Isr ratio (inner ratio) per Source
    df_hardship_ratio = df_hardship.copy()


    i = 0
    for src in sorted_sources: 

        temp_row = (df_hardship.iloc[i,:] / df_hardship.iloc[i+1,:] ).round(1).to_frame().T

        temp_row['Source'] = src

        temp_row['Side'] = 'Comparing_Sides'

        temp_row = temp_row.set_index(['Source','Side'])

        df_hardship_ratio = pd.concat([df_hardship_ratio,temp_row])

        i = i + 2


    # Sort rows
    a_T2_Hardship_count = df_hardship_ratio.reset_index().sort_values(['Source','Side'],ascending=[True, False]).reset_index(drop=True).fillna(0)

    a_T2_Hardship_count['Year'] = conflict_year
    
    tables_p2.append(df_hardship_simple)
    
    df_hardship_simple.to_csv(path_past_conflict_agg_data + "IG_Prompt_2_Hardship_Label_Counts_Conflict_{}.csv".format(conflict_year))


#%%% Plot Stacked Barplots


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

# 0. Switches
plot_font = 20
hardship_label = ['Casualties']
plot_manual_legend = True

# Create a dataframe to combine the conflict datasets
df_cas_ratio = pd.DataFrame()

# Go over each conflict year
for conflict_year in [2008, 2012, 2014, 2023]:
    # 1. Data Preparation: Hardship Label Counts 
    a_T2_raw = pd.read_csv(path_past_conflict_agg_data + "IG_Prompt_2_Hardship_Label_Counts_Conflict_{}.csv".format(conflict_year)) 

    #-alrt
    a_T2_raw["Source"] = a_T2_raw["Source"].replace(dict_sources)
    
    # Limit the data to the selected hardships
    a_T2_raw['Hardship'] = a_T2_raw['Hardship'].apply(lambda x: x if x in hardship_label else "Other")
    a_T2_raw = a_T2_raw.groupby(['Source','Side','Hardship'])['Instance_Count'].sum().reset_index()
    
    a_T2_raw = a_T2_raw[a_T2_raw['Hardship'] != 'Other'].copy()
    
    # Sort the data to preserve data order
    a_T2_raw = a_T2_raw.sort_values(['Source','Side','Hardship'], ascending=[True, False, True])
    
    # Combine the Casualty data 
    df_temp = a_T2_raw.reset_index(drop=True).copy()
    df_temp['Year'] = conflict_year
    df_cas_ratio = pd.concat([df_cas_ratio, df_temp])


# Combine 2008-2012 data
df_cas_ratio_comb = df_cas_ratio[df_cas_ratio['Year'].isin([2008, 2012])]
df_cas_ratio_comb = df_cas_ratio_comb.groupby(['Source','Side'])['Instance_Count'].sum().reset_index()       
df_cas_ratio_comb['Year'] = '2008-2012'

df_cas_ratio_comb = pd.concat([df_cas_ratio_comb, df_cas_ratio[~df_cas_ratio['Year'].isin([2008, 2012])]])
df_cas_ratio_comb = df_cas_ratio_comb.drop('Hardship', axis=1)

# Define the label for the actual shares bar
actual_label = 'ACTUAL'

# Create dataset to contain the actual combined casualty counts
df_cas_actual = pd.DataFrame({
    "Side": ['Israel', 'Palestine', 'Israel', 'Palestine', 'Israel', 'Palestine'],
    "Instance_Count": [413, 8322, 1606, 12693, 6800, 139700],
    'Year': ['2008-2012', '2008-2012', '2014', '2014', '2023', '2023']
})
df_cas_actual['Source'] = actual_label

# Combine with the Instance Counts dataset
df_cas_ratio_comb_actual = pd.concat([df_cas_ratio_comb, df_cas_actual])
df_cas_ratio_comb_actual = df_cas_ratio_comb_actual.rename(columns={"Instance_Count": "Instance_Casualty_Count"})
df_cas_ratio_comb_actual = df_cas_ratio_comb_actual.reset_index(drop=True)
df_cas_ratio_comb_actual['Year'] = df_cas_ratio_comb_actual['Year'].astype(str)

# Plot the Stacked Barplot

sns.set_theme(style="whitegrid")

# Get unique years to determine subplots
years = df_cas_ratio_comb_actual['Year'].unique()

# Initialize the stacked figure (3 rows, 1 column)
# sharex=True hides the x-axis text on the top two plots
fig, axes = plt.subplots(nrows=len(years), ncols=1, figsize=(10, 15), sharex=True)

# Modify color dicts outside the loop
color_dict_isr = dict(zip(sorted_sources, [dict_colors['Israel']] * len(sorted_sources)))
color_dict_isr[actual_label] = 'black'

color_dict_pal = dict(zip(sorted_sources, [dict_colors['Palestine']] * len(sorted_sources)))
color_dict_pal[actual_label] = dict_colors['Oct_7_Label']

# Loop over each year
for conflict_year, ax in zip(years, axes):
    
    df_cas_ratio_piv = df_cas_ratio_comb_actual[df_cas_ratio_comb_actual['Year'] == conflict_year]
    df_cas_ratio_piv = df_cas_ratio_piv.pivot(index='Side', columns='Source', values='Instance_Casualty_Count').T


    df_cas_ratio_piv['Total'] = df_cas_ratio_piv['Israel'] + df_cas_ratio_piv['Palestine']
    df_cas_ratio_piv['Isr_ratio'] = 100
    df_cas_ratio_piv['Pal_ratio'] = round(100 * df_cas_ratio_piv['Palestine'] / df_cas_ratio_piv['Total'], 1)

    # Standard sorting, "ACTUAL" will automatically be placed first
    df_cas_ratio_piv = df_cas_ratio_piv.reset_index()
    df_cas_ratio_piv = df_cas_ratio_piv.sort_values('Source')

    # Plot the Isr Ratios (100)
    sns.barplot(y="Isr_ratio", x="Source", data=df_cas_ratio_piv, ax=ax,
                label="Israel", palette=color_dict_isr, hue="Source", legend=False)
    
    # Plot the Pal Ratios
    sns.barplot(y="Pal_ratio", x="Source", data=df_cas_ratio_piv, ax=ax,
                label="Palestine", palette=color_dict_pal, hue="Source", legend=False)
    
    # Clean and label axes
    ax.set_xlabel("")
    
    # Set the y-axis label to the conflict year
    ax.set_ylabel(conflict_year, fontsize=plot_font + 5, fontweight="bold", labelpad=20)
    
    ax.tick_params(axis='both', labelsize=18)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
        
    # Add a % next to the y-axis ticks
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
    
    sns.despine(ax=ax, left=True, right=True, top=True, bottom=True)

# Add a main legend
if plot_manual_legend:
    legend_elements = [
        Patch(facecolor='black', label='Israel - Actual Casualty Share'),
        Patch(facecolor=dict_colors['Oct_7_Label'], label='Palestine - Actual Casualty Share'),
        Patch(facecolor=dict_colors['Israel'], label='Israel - Share of Casualty Mentions'),
        Patch(facecolor=dict_colors['Palestine'], label='Palestine - Share of Casualty Mentions'),
    ]
    
    # Attach legend to the entire figure at the top
    fig.legend(
        handles=legend_elements,
        loc='upper left',              # Anchors the top-left of the legend box...
        bbox_to_anchor=(1.01, 1),   # ...just to the right (1.01) and near the top (0.95) of the plot
        ncol=1,                        # Forces everything into a single column
        frameon=False,
        fontsize=18
    )

# Clean up layout spacing
plt.tight_layout()

# Export combined plot as svg

title_i = 'Supp Fig 13 - Actual casualty counts and individualized casualty-related story percentages per side for each media source.svg'
plt.savefig(path_report + title_i, format='svg',  bbox_inches='tight')
    


#%% Supp Fig 14

print("\nGenerating Supp Fig 14")


#%%% Generate Data


# Import the CS P1 Data
df_cs_cd_all = pd.read_csv(path_response_CVN_prompt_1_past)

df_cs_cd_all = df_cs_cd_all.rename(columns = {'Side':'Side_new', 'Sentence':'Full_Sent'}).copy()


# CLAIM ANALYSIS

for conflict_year in [2014]:
    
    print("\nProcessing data of conflict:", conflict_year)
    
    df_cs_cd = df_cs_cd_all[df_cs_cd_all['Conflict_Year'] == conflict_year].copy()   

    filter_claims = df_cs_cd['Full_Sent'].str.contains("claim", case=False)

    keep_cols = ['Source','Article_ID','Keyword','Statistics', 'Association','Side_new','Full_Sent']

    df_claims_raw = df_cs_cd.loc[filter_claims,keep_cols]

    #df_claims_raw.to_csv("05- Analysis/" + "Casting Doubt - Claims Analysis - 01- Unclassified - {}.csv".format(conflict_year))

    """


    # read manually classified df_claims dataset
    #df_claims = pd.read_excel(analysis_cast_doubt_path + "Casting Doubt - Claims Analysis - 02- Classified.xlsx")
    df_claims = pd.read_excel(analysis_cast_doubt_path  + "Casting Doubt - Claims Analysis - Manually Classified.xlsx")

    # remove irrelevant claim phrases
    filter_flag = df_claims['Flag']==2
    df_claims = df_claims[filter_flag]

    # remove duplicated claim phrases
    df_claims = df_claims.drop_duplicates(['Article_ID','Side_new','Full_Sent','Doubted Source Claim Side'])
    df_table_5 = df_claims.groupby(['Source','Side_new','Doubted Source Claim Side'])['Article_ID'].count()
    df_table_5 = df_table_5.reset_index()
    df_table_5.columns = ['Source', 'Victim Side',	'Doubted Source Side', 'Count']

    df_table_5 = df_table_5.sort_values(by=['Source', 'Victim Side',	'Doubted Source Side'],
                                                    ascending = [True, False, False])

    # Export
    df_table_5.to_excel(analysis_cast_doubt_path + "Claims_Report.xlsx")
    """

df_claims_raw = df_claims_raw.drop_duplicates(['Article_ID','Full_Sent'])


# Manual valid Claim counts
df_claim_counts ={
    
    "2008": {'Phrases': ['claim'],
                 'AJE_Total_Num_of_Stats_About_Victims':  [0],
                 'AJE_Referencing_Palestinian_Victims':   [0],
                 'AJE_Referencing_Israeli_Victims':       [0],
                 'BBC_Total_Num_of_Stats_About_Victims':  [0],
                 'BBC_Referencing_Palestinian_Victims':   [0],
                 'BBC_Referencing_Israeli_Victims':       [0],
                 'CNN_Total_Num_of_Stats_About_Victims':  [0],
                 'CNN_Referencing_Palestinian_Victims':   [0],
                 'CNN_Referencing_Israeli_Victims':       [0],
                 'NYT_Total_Num_of_Stats_About_Victims':  [0],
                 'NYT_Referencing_Palestinian_Victims':   [0],
                 'NYT_Referencing_Israeli_Victims':       [0],
                 'CD_Type': ['Uncertainty in Numbers']},
    
    "2012": {'Phrases': ['claim'],
                 'AJE_Total_Num_of_Stats_About_Victims':  [0],
                 'AJE_Referencing_Palestinian_Victims':   [0],
                 'AJE_Referencing_Israeli_Victims':       [0],
                 'BBC_Total_Num_of_Stats_About_Victims':  [0],
                 'BBC_Referencing_Palestinian_Victims':   [0],
                 'BBC_Referencing_Israeli_Victims':       [0],
                 'CNN_Total_Num_of_Stats_About_Victims':  [0],
                 'CNN_Referencing_Palestinian_Victims':   [0],
                 'CNN_Referencing_Israeli_Victims':       [0],
                 'NYT_Total_Num_of_Stats_About_Victims':  [0],
                 'NYT_Referencing_Palestinian_Victims':   [0],
                 'NYT_Referencing_Israeli_Victims':       [0],
                 'CD_Type': ['Uncertainty in Numbers']},
    
    
    "2014": {'Phrases': ['claim'],
                 'AJE_Total_Num_of_Stats_About_Victims':  [0],
                 'AJE_Referencing_Palestinian_Victims':   [0],
                 'AJE_Referencing_Israeli_Victims':       [0],
                 'BBC_Total_Num_of_Stats_About_Victims':  [0],
                 'BBC_Referencing_Palestinian_Victims':   [0],
                 'BBC_Referencing_Israeli_Victims':       [0],
                 'CNN_Total_Num_of_Stats_About_Victims':  [1],
                 'CNN_Referencing_Palestinian_Victims':   [1],
                 'CNN_Referencing_Israeli_Victims':       [0],
                 'NYT_Total_Num_of_Stats_About_Victims':  [0],
                 'NYT_Referencing_Palestinian_Victims':   [0],
                 'NYT_Referencing_Israeli_Victims':       [0],
                 'CD_Type': ['Uncertainty in Numbers']}, 
}


for conflict_year in [2008, 2012, 2014]:
    print("\nProcessing data of conflict:", conflict_year)
    
    df_cs_cd = df_cs_cd_all[df_cs_cd_all['Conflict_Year'] == conflict_year].copy()


    #print("\nGenerating Table 6")

    # 1. Clean the dataset: Since a sentence can contain more than one instance
    #    then we need to drop duplicated sentences
    #    

    df_cs_cd_uniq = df_cs_cd.drop_duplicates(['Article_ID','Side_new','Full_Sent']).copy()

    # 2. Simplify the resulting dataset
    df_cs_cd_uniq = df_cs_cd_uniq[['Article_ID', 'Source', 'Side_new','Full_Sent']].copy()


    # 3. import the list of highly critical phrases (I added the claims keyword here)
    df_table_6 = pd.read_excel(cd_phrases_path)

    # 4. Clean the phrases
    df_table_6.loc[:,'Phrases'] = df_table_6['Phrases'].str.replace(".","").str.replace(",","").str.replace("â€¦","").str.strip()

    
    # 4.x Create a dictionary to specify the CD Phrase type after creating the 
    #     counts table below
    
    df_table_6_dict = df_table_6.copy()

    df_table_6 = df_table_6.drop(["CD_Type"], axis=1)
    
    
    # 5. loop over the sources

    for source_i in sorted_sources:
        
        cvn_counts = df_cs_cd[df_cs_cd['Source']==source_i].shape[0]

        print("\n   {} : {}".format(source_i,cvn_counts))
        
        source_cs_full_sent = df_cs_cd_uniq[df_cs_cd_uniq['Source']==source_i]

        # Create a Pal instances df
        pal_df = source_cs_full_sent[source_cs_full_sent['Side_new']=="Palestine"].copy()

        # Create an Isr instances df
        isr_df = source_cs_full_sent[source_cs_full_sent['Side_new']=="Israel"].copy()

        source_df = pd.DataFrame()
        list_pal  = []
        list_isr  = []
        list_tot  = []

        for i, row in df_table_6.iterrows():

            phrase = row['Phrases'].strip()
            phrase = phrase + "|" + phrase.replace("-"," ")

            pal_counts = pal_df['Full_Sent'].str.replace("-"," ").str.contains(phrase, regex=True, case=False).sum()
            isr_counts = isr_df['Full_Sent'].str.replace("-"," ").str.contains(phrase, regex=True, case=False).sum()

            list_tot.append(pal_counts + isr_counts)
            list_pal.append(pal_counts)
            list_isr.append(isr_counts)

        source_df = pd.DataFrame({"Total":list_tot,
                                  "Count_Pal": list_pal,
                                  "Count_Isr": list_isr,
                                  })

        source_df['Percent_Pal'] =  source_df.apply(lambda x: x['Count_Pal']/x['Total'] if x['Total']!=0 else 0, axis=1)
        source_df['Percent_Isr'] =  source_df.apply(lambda x: x['Count_Isr']/x['Total'] if x['Total']!=0 else 0, axis=1)

        source_df['Percent_Pal'] = (100 * source_df['Percent_Pal']).round(1)
        source_df['Percent_Isr'] = (100 * source_df['Percent_Isr']).round(1)


        source_df['count_percent_pal'] = source_df.apply(lambda x: str(int(x['Count_Pal'])) +' (' + str(x['Percent_Pal']) +")", axis=1)
        source_df['count_percent_isr'] = source_df.apply(lambda x: str(int(x['Count_Isr'])) +' (' + str(x['Percent_Isr']) +")", axis=1)

        source_df['count_percent_pal'] = source_df['Count_Pal']
        source_df['count_percent_isr'] = source_df['Count_Isr']


        source_df = source_df[['Total', 'count_percent_pal', 'count_percent_isr']].copy()


        source_df.columns = [
                            source_i+"_Total_Num_of_Stats_About_Victims",
                            source_i+"_Referencing_Palestinian_Victims",
                            source_i+"_Referencing_Israeli_Victims",
                            ]

        df_table_6 = pd.concat([df_table_6, source_df], axis=1)


    # Specify the Casting Doubt Category
    #df_table_6['CD_Type'] = df_table_6.reset_index()['Phrases'].apply(lambda x: "Uncertainty in Number" if (x=="reportedly")|(x=='was reported to have')|(x=='claim') else "Source Doubting")
    df_table_6 = df_table_6.merge(df_table_6_dict, on = 'Phrases', how = 'left')

    
    # Manulally add the "Claim"-containing phrases under "Uncertainty in Numbers"
    df_claims = df_claim_counts [str(conflict_year)]

    df_claims = pd.DataFrame.from_dict(df_claims)

    df_table_6 = pd.concat([df_table_6, df_claims])
    
    

    # 6. Implement a manual fix to set all 'Source Doubting' Isr cols to 0 since
    #    the CD phrases do not refer to Israel but are mainly Hamas-related
    filter_cols = df_table_6.filter(regex= "Referencing_Israeli_Victims", axis = 'columns').columns

    #filter_cd_type = df_table_6['CD_Type']=='Source Doubting'
    filter_cd_type = df_table_6['Phrases'].str.contains("Hamas")

    df_table_6.loc[filter_cd_type, filter_cols] = 0

    df_table_6 = df_table_6.set_index('Phrases')
    
    # Calculate the total columns as sum of Pal and Isr Counts
    for i in [0,3,6,9]:
        df_table_6.iloc[:,i] = df_table_6.iloc[:,i+1] + df_table_6.iloc[:,i+2]

        
    # Export Counts for all 4 sources per side + totals
    title_i = "CVN - Casting Doubt Aggregate Data - {}.csv".format(conflict_year)
    
    df_table_6.to_csv(path_past_conflict_agg_data + title_i)
    
    
    
#%%% Plot Barplots


# [1] Import CVN response data - Conflict of 2023

df_cs_counts = pd.read_csv(path_response_CVN_prompt_1_2023)
df_cs_counts['Source'] = df_cs_counts['Source'].map(dict_sources)
df_cs_counts = df_cs_counts[['Source','Side_new','Instance_ID']].copy()
df_cs_counts['Conflict_Year'] = 2023
df_cs_counts = df_cs_counts.rename(columns = {'Side_new':"Side"})


# [1] Import CVN response data - Conflicts of  2008, 2012, 2014
df_cs_past_counts = pd.read_csv(path_response_CVN_prompt_1_past)
df_cs_past_counts = df_cs_past_counts.rename(columns = {'Side_new':"Side"})

df_cs_past_counts = df_cs_past_counts[['Source','Instance_ID','Side','Conflict_Year']].copy()


# -  Combine both datasets
df_cs_all_counts = pd.concat([df_cs_counts, df_cs_past_counts])


# -  Count the # of CVNs pr Source per Side per Conflict
df_cs_all_counts = df_cs_all_counts.groupby(['Conflict_Year','Source','Side'])['Instance_ID'].count().reset_index()

df_cs_all_counts = df_cs_all_counts.rename(columns = {'Instance_ID':"CS_Instance_Counts"})


# -  Combine the 2008 and 2012 conflict data
a = df_cs_all_counts[df_cs_all_counts['Conflict_Year']==2008].reset_index(drop=True)
b = df_cs_all_counts[df_cs_all_counts['Conflict_Year']==2012].reset_index(drop=True)
c = df_cs_all_counts[df_cs_all_counts['Conflict_Year']==2014].reset_index(drop=True)
d = df_cs_all_counts[df_cs_all_counts['Conflict_Year']==2023].reset_index(drop=True)


a['CS_Instance_Counts'] = a['CS_Instance_Counts'] + b['CS_Instance_Counts'] 

a['Conflict_Year'] = '2008_2012'

df_counts = pd.concat([a,c,d]).reset_index(drop=True)

df_counts['Conflict_Year'] = df_counts['Conflict_Year'].astype(str)




#### PART 2: IMPORT CD COUNTS DATASETS


# -  Import the Past Conflict CD Phrase Counts
title_i = "CVN - Casting Doubt Aggregate Data - {}.csv"

df_cd_counts_2008 = pd.read_csv(path_past_conflict_agg_data + title_i.format(2008))
df_cd_counts_2012 = pd.read_csv(path_past_conflict_agg_data + title_i.format(2012))
df_cd_counts_2014 = pd.read_csv(path_past_conflict_agg_data + title_i.format(2014))

# -  Merge Conflicts 2008 and 2012
df_cd_counts_08_12 = df_cd_counts_2008.copy()

df_cd_counts_08_12.iloc[:,1:-1] = df_cd_counts_2008.iloc[:,1:-1] + df_cd_counts_2012.iloc[:,1:-1]


# -  Import the 2023 Conflict CD Phrase Counts
df_cd_counts_2023 = pd.read_csv(path_past_conflict_agg_data + "CVN - Casting Doubt Aggregate Data - 2023.csv")




#### PART 3: Standardize, Merge, Transform and Calculate % of CD/CS

# -  Standardize the col names
#    the 2023 data used the full name of the source instead of abbreviation
#    i.e. Al Jazeera English instead of AJE (Past Conflicts)
df_cd_counts_2023.columns = df_cd_counts_2008.columns 


# -  Clean Datasets - keep relevant columns only 
#    (just CD counts per side)

keep_cols = [i for i in df_cd_counts_2008.columns if ("Total" not in i) & ("Phrases" not in i)]
    
df_cd_counts_08_12 = df_cd_counts_08_12[keep_cols].copy()

df_cd_counts_2014  = df_cd_counts_2014 [keep_cols].copy()

df_cd_counts_2023  = df_cd_counts_2023 [keep_cols].copy()

    
# -  Extract Source + Side of the data then transform it
sum_cols = [x for x in keep_cols if x != "CD_Type"]

def transform_cd_count_tables(data):
    
    # -  count num of CD phrases per CD category/type
    data = data.groupby('CD_Type')[sum_cols].sum().T.reset_index()
    
    # -  extract source 
    data['Source'] = data['index'].apply(lambda x: x.split("_")[0])
    
    # -  extract side 
    side_dict = {"Palestinian":"Palestine", "Israeli":"Israel"}

    data['Side']   = data['index'].apply(lambda x: x.split("_")[2])

    data['Side']  = data['Side'].map(side_dict)
    
    # -  clean output
    data = data.drop(['index'], axis = 1)
    
    data = data[['Source', 'Side', 'Source Doubting', 'Uncertainty in Numbers']]
        
    # -  transform output
    data = data.melt(
        id_vars= ["Source",'Side'],
        value_vars=["Source Doubting", "Uncertainty in Numbers"],
        var_name="Type",
        value_name="CD_Phrase_Counts"
    )
    
    # -  prepare column to differentiate data for the plot colors
    data['Side_Type'] = data['Type'] + " (" + data['Side'] + ")"
    
    # -  limit dataset to relevant columns
    data = data[['Source', 'Side','Side_Type', 'CD_Phrase_Counts']]
        
    return data.copy()


df_cd_counts_08_12_T = transform_cd_count_tables(df_cd_counts_08_12)
df_cd_counts_08_12_T['Conflict_Year'] = '2008_2012'

df_cd_counts_2014_T  = transform_cd_count_tables(df_cd_counts_2014)
df_cd_counts_2014_T['Conflict_Year'] = '2014'

df_cd_counts_2023_T  = transform_cd_count_tables(df_cd_counts_2023)
df_cd_counts_2023_T['Conflict_Year'] = '2023'


# -  Merge CS and CD Data
df_cd_counts_08_12_T = df_cd_counts_08_12_T.merge(df_counts, on = ['Conflict_Year', 'Source', 'Side'])
df_cd_counts_2014_T  = df_cd_counts_2014_T.merge(df_counts,  on = ['Conflict_Year', 'Source', 'Side'])
df_cd_counts_2023_T  = df_cd_counts_2023_T.merge(df_counts, on = ['Conflict_Year', 'Source', 'Side'])


# -  Calculate Percentage of CD of CS
df_cd_counts_08_12_T['CD_Phrase_Percent'] = np.round(100*df_cd_counts_08_12_T['CD_Phrase_Counts']/df_cd_counts_08_12_T['CS_Instance_Counts'],1)
df_cd_counts_2014_T['CD_Phrase_Percent'] = np.round(100*df_cd_counts_2014_T['CD_Phrase_Counts']/df_cd_counts_2014_T['CS_Instance_Counts'],1)
df_cd_counts_2023_T['CD_Phrase_Percent'] = np.round(100*df_cd_counts_2023_T['CD_Phrase_Counts']/df_cd_counts_2023_T['CS_Instance_Counts'],1)



#### PART 4: Plot the Data

# Barplot Code - % of CVNs with Doubt Casting Statements - 4 Bars per Source


import seaborn as sns
import matplotlib.pyplot as plt

# Get the max Y axis label
y_max = max(pd.concat([df_cd_counts_08_12_T['CD_Phrase_Percent'],
                       df_cd_counts_2014_T ['CD_Phrase_Percent'],
                       df_cd_counts_2023_T ['CD_Phrase_Percent']]))

#y_max = 5
y_axis_tick_steps = 5

sns.set_theme(style="white")

dfs = [
    df_cd_counts_08_12_T,
    df_cd_counts_2014_T,
    df_cd_counts_2023_T
]


# Set the titles of each subplot (can be removed in loop)
titles = ['2008 & 2012', '2014', '2023']

fig, axes = plt.subplots(
    nrows=3,
    ncols=1,
    sharex=True,
    figsize=(10, 10)
)

for ax, df,title in zip(axes, dfs, titles):
    
    # -  add artificial blanks between the bars

    df2 = df.drop_duplicates(['Source', 'Side']).copy()
    df2['Source'] = df2['Source'].apply(lambda x: x+"2")
    df2['CD_Phrase_Percent'] = 0
    df2 = df2[~df2['Source'].str.contains('NYT')].copy()
    
    df = pd.concat([df,df2])
    
    df = df.sort_values(['Source','Side','Side_Type'])
    
    sns.barplot(
        data=df,
        x="Source",
        y="CD_Phrase_Percent",
        hue="Side_Type",
        palette=dict_colors,
        errorbar=None,
        ax=ax
    )
    
    # -  specify single unified y axis ax value
    ax.set_ylim(top=y_max)
    
    # -  specify the title of each subplot
    #ax.set_title(title, fontweight="bold")
    ax.set_title("", fontweight="bold")

    
    # -  remove the yaxis label of each subplot as we will use a single
    #    unified one instead
    ax.set_ylabel("")

    # -  completely remove any legends as we will use a single unified one
    if ax.legend_ is not None:
        ax.legend_.remove()
        
    # -  modify the y axis tick params and label size
    ax.tick_params(axis="y", labelsize=14)
    for label in ax.get_yticklabels():
       label.set_fontweight("bold")
       
    # -  add bar numbers over bars
    
    for container in ax.containers:
        ax.bar_label(
            container,
            padding=3,
            fontsize=11,
            fontweight="bold",
            #labels=[f"{v:.1f}%" for v in container.datavalues],
        )


# Add a Unified Legend

# -  get the labels
handles, labels = axes[0].get_legend_handles_labels()

# -  sort the labels (ascending)
labels, handles = zip(*sorted(zip(labels, handles)))

# -  plot the labels

fig.legend(
    handles,
    labels,
    loc="upper center",
    ncol=2,
    frameon=False,
    
    fontsize=16,          # increase size
    prop={"weight": "bold"}  # make bold
)


# Unified Y Axis Label: Add 
fig.supylabel("% of CVN Statements containing Casting Doubt phrases",
              fontweight="bold",
              fontsize=18,
              x= 0 # the small the # the more left it goes
              )

# Unified X Axis Label: Remove 
axes[-1].set_xlabel("")

# Set the Tick size of the x and y axes
import matplotlib.ticker as mticker

for ax in axes:
    ax.yaxis.set_major_locator(mticker.MultipleLocator(y_axis_tick_steps))
    
    ax.tick_params(axis="x", labelsize=6)
    
    
    
# tweak the plot
sns.despine()
plt.tight_layout(rect=[0, 0, 1, 0.97])  # leave space for legend

fig.subplots_adjust(hspace=0.22) # hspace is a fraction of avg subplot height



# Export the plot
title_i = 'Supp Fig 14 - Share of CVN instances containing Casting Doubt phrases per Type and Side and Source.svg'
plt.savefig(path_report + title_i, format='svg',  bbox_inches='tight')

plt.show()


