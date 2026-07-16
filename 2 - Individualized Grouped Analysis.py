#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# %% ---------------------------

#%% Overview

"""
The code below generates the following list of figures and tables:
    
    
    Main Figures
    
    Fig 2 Results of Individualized vs. Category-based Reporting Analysis.
          
          This figure is divided into the following subplots:
              
              
          - Fig 2A: Ratio of Individualized to Grouped mentions per side for 
                    each media source
            
          - Fig 2B - Left: Individualized casualty-related story counts
                           per side for each media source.  
                   
            Fig 2B - Right: Actual casualty counts for both sides in the first 
                            12 months. 
                            
          - Fig 2C: Proportion of Western media’s Israeli casualty stories 
                    mentioning Oct 7 or hostages.
                    
                    
           - Fig 2D: Weekly average diff in Vividness of Emotions scores across 
                     media source during the first 12 months.
                     
    
    Supplementary Figures
    
    
    Supp Fig 3: Individualized instance counts by hardship category.
                
    
    Supp Fig 4: Correlation between Palestinian civilian deaths and Israeli 
                story coverage
                
                
    Supp Fig 5: Plot Volume difference score across all media sources. 
                


    Supplementary Tables
    
    
    Supp Tab 3: Count of Individualized and Grouped Instances. 
                
                
    Supp Tab 4: Count of Western Media’s Individualized Hardshiprelated Stories 
                per Side per Source for four major events
                
                
    Supp Tab 5: Child-related Individualized Stories
                

"""

# %% ---------------------------
# %% INPUT
# %% ---------------------------


#%% Libraries

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.patches as mpatches
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import interpolate
from datetime import datetime, timedelta



# %% Switches


analyze_prompt_2_conc_rep   = False

analyze_prompt_empathy      = True

analyze_prompt_empathy_time = True



# %% Paths

# Primary Data
path_primary_data            = "01- Primary Data/df_primary.csv"


# Secondary Data
path_plot_colors             = "02- Secondary Data/02- Project Plotting Colors.xlsx"

path_critical_events         = '02- Secondary Data/03- Conflict Events.xlsx'


# Response Data

path_prompt_1_IG_instances   = '03- LLM Response Data/Response Data - Individualized-Grouped - P1 - Find Hardship Instances.csv'

path_prompt_2_hardship_label = '03- LLM Response Data/Response Data - Individualized-Grouped - P2 - Label Hardship Instances.csv'

path_prompt_3_child_label    = '03- LLM Response Data/Response Data - Individualized-Grouped - P3 - Label Children.csv'

path_empathy_vivid_emotions  = '03- LLM Response Data/Response Data - Individualized-Grouped - Empathy - Vivid Emotions.csv'

path_empathy_plot_volume     = '03- LLM Response Data/Response Data - Individualized-Grouped - Empathy - Plot Volume.csv'


# Aggregated Data
path_past_conflict_agg_data  = "04- Past Conflict Aggregated Data/"

# Output - Data
path_report                  = '05- Report Plots and Tables/'


# %% Dictionaries

dict_colors  = pd.read_excel(path_plot_colors, usecols = ["Entity","Color"])

dict_colors  = dict_colors.dropna().set_index('Entity')['Color'].to_dict()

dict_sources = { "Al Jazeera English":"AJE", 
                "BBC":"BBC",
                "CNN Wire": "CNN", 
                "The New York Times":"NYT" }
     
sorted_sources = list(dict_sources.keys())
sorted_sources.sort()

# %% Functions

#   A data-smoothing function
def smooth_plot (data, res = 1000):

    smoothed_data = pd.DataFrame({'Date':[]})

    for col in data:

        temp_df = data[col].copy()
        temp_df = temp_df.dropna()
        dates = temp_df.index
        dates = dates.astype('datetime64[s]').astype(np.int64)

        x = dates
        y = temp_df.to_list()
        interp_fn = interpolate.interp1d(x, y, kind='cubic')

        xnew = np.arange(dates[0], dates[-1], res)
        ynew = interp_fn(xnew)

        data_new = pd.DataFrame(ynew, index=xnew).reset_index()
        data_new.columns = ['Date',temp_df.name]
        data_new['Date'] = pd.to_datetime(data_new['Date'],unit='s').copy()
        smoothed_data = smoothed_data.merge(data_new, on='Date', how='outer')

    smoothed_data['Date'] = smoothed_data['Date'].apply(lambda x: x.date())
    smoothed_data = smoothed_data.set_index('Date')

    return smoothed_data




# %% ---------------------------
# %% DATA
# %% ---------------------------


# %% Import Primary Data 

# - all articles 

df_primary = pd.read_csv(path_primary_data, usecols = ['Article_ID', 'Date', 'Source'])

df_primary['Date'] = pd.to_datetime(df_primary['Date'], format = "%d %B %Y")


# %% Import Response Data

# - Prompt 1 Response - IG Instances

df_prompt_1 = pd.read_csv(path_prompt_1_IG_instances)

df_prompt_1['Phrases'].apply(lambda x: len(x)).max()

df_prompt_1['Date'] = pd.to_datetime(df_prompt_1['Date'], format = "%Y-%m-%d")


# - Prompt 2 Response - Hardship Label
                        
df_prompt_2 = pd.read_csv(path_prompt_2_hardship_label)
    

# - Prompt 3 Response - Child Label

df_child_raw = pd.read_csv(path_prompt_3_child_label)


# - Empathy-Vividness Response

df_voe = pd.read_csv(path_empathy_vivid_emotions)


# - Empathy-Plot Vol Response

df_pvol = pd.read_csv(path_empathy_plot_volume)




# %% Merge & Clean Data

# - merge Prompt 2 & Empathy Responses

df_hard_emp = df_prompt_2.merge(df_voe)

df_hard_emp = df_hard_emp.rename(columns = {'Rating':'Vividness_of_Emotions'})

df_hard_emp = df_hard_emp.merge(df_pvol)

df_hard_emp = df_hard_emp.rename(columns = {'Rating':'Plot_Volume'})


# - clean merged data

# -  convert date col to datetime
df_hard_emp['Date'] = pd.to_datetime(df_hard_emp['Date'], format = "%Y-%m-%d")


# -  double check - remove duplicate entities
df_hard_emp = df_hard_emp.drop_duplicates(['Article_ID','Entity','Side'])


# - keep Civilian entities
df_hard_emp['Civilian_Status'] = df_hard_emp['Civilian_Status'].apply(lambda x: "Non-Civilian" if (x=="Military") | (x=="Government") else x)

df_hard_emp = df_hard_emp[df_hard_emp['Civilian_Status']=='Civilian'].copy()


# -  filter location - Gaza/Israel
df_hard_emp = df_hard_emp[df_hard_emp['Location'].str.contains('Gaza|Israel', case=False)].copy()



# %% ---------------------------
# %% Prompt 1: IG Counts
# %% ---------------------------

# %% Clean Data - Indiv

# Initial Filtering

# -  keep only individualized instances
df_indiv = df_prompt_1[df_prompt_1['Type']=="Individualized"].copy()


# -  filter side = Pal / Isr 

filter_side = df_indiv['Side'].isin(['Palestine','Israel'])

df_indiv = df_indiv[filter_side].copy()


# -  keep only Primary/Secondary entities

df_indiv_prim = df_indiv[df_indiv['Primary']=="Yes"].copy()

df_indiv_sec  = df_indiv[df_indiv['Primary']=="No"].copy()



# -  remove duplicate entities
#df_indiv_prim = df_indiv_prim.groupby(['Article_ID','Entity', 'Side','Civilian_Status', 
#                   'Date', 'Source', 'Article','Location'])['Phrases'].apply(set).reset_index()

df_indiv_prim = df_indiv_prim.groupby(['Article_ID','Entity', 'Side','Civilian_Status', 
                   'Date', 'Source'          ,'Location'])['Phrases'].apply(set).reset_index()


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



# %% Clean Data - Group

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




# %% Supp Tab 3

print("\nGenerating Supp Tab 3")


# Generate Individualized - Grouped Instance Count Ratios

count_ind = df_indiv.groupby(['Source','Side'])['Article_ID'].count()


count_grp = df_group.groupby(['Source','Side'])['Article_ID'].count()


count_ind_grp = count_ind.reset_index().merge(count_grp.reset_index(), on = ['Source','Side'])

count_ind_grp = count_ind_grp.rename(columns={'Article_ID_x':'Indiv_Counts',
                                              'Article_ID_y': 'Group_Counts'})


df_table_1 = ((count_ind/count_grp)).round(2).reset_index().sort_values(['Source','Side'],ascending=[True, False]).reset_index(drop=True)

df_table_1 = df_table_1.rename(columns={'Article_ID':'Indiv_to_Group_Ratio'})

df_table_1 = count_ind_grp.merge(df_table_1, on = ['Source','Side'])

a_T1_IG_Ratios = df_table_1.sort_values(['Source','Side'], ascending = [True, False])

a_T1_IG_Ratios['Source'] = a_T1_IG_Ratios['Source'].apply(lambda x: dict_sources[x])


# Export 
df_supp_tab_3 = a_T1_IG_Ratios.copy()

title_i = "Supp Tab 3 - Count of Individualized and Grouped Instances"

df_supp_tab_3.to_csv(path_report + title_i + '.csv')


# - export an extra copy for the past conflicts analysis figures
title_i = "IG_Prompt_1_Instance_Counts_Ratios_Conflict_2023.csv"

df_supp_tab_3.to_csv(path_past_conflict_agg_data + title_i)


# %% GEE Regression

print("\nGenerating GEE regression results")

# Perform the GEE Logistic Regression for dependent instances

# Import the libraries
import statsmodels.api as sm
from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.genmod import families


# Define output file name to export the results as a text file
#output_file_name = path_report + 'Indiv_Group_GEE_Regression_Results.txt'
output_file_name = path_report + 'Fig 2A - GEE Regression Results.txt'


# Instantiate an empty string to hold all the summary tables
gee_results_txt = ""


# 1. Obtain the cleaned df_prompt_1 data via combining df_indiv & df_group
df_gee = df_indiv[['Source', 'Article_ID', 'Side']].copy()

df_gee['Type'] = 'Individualized'

df_gee = pd.concat([df_gee,df_group[['Source','Article_ID', 'Side', 'Type']].copy()])


# 2. Convert the categorical data to numeric representations
df_gee['type_numeric'] = df_gee['Type'].map({'Grouped': 0, 'Individualized': 1})

df_gee['side_numeric'] = df_gee['Side'].map({'Israel': 0, 'Palestine': 1})


# 3. Filter the data by source    
for src_i in sorted_sources:
    
    running_title = "Source: " + src_i + "\n\n\n"
    
    #print(running_title)
    
    df_gee_src = df_gee[df_gee['Source']==src_i].copy()


    # Run the GEE
    endog = df_gee_src['type_numeric']
    exog = sm.add_constant(df_gee_src['side_numeric'])
    groups = df_gee_src['Article_ID']
    
    model = GEE(
        endog=endog,
        exog=exog,
        groups=groups,
        family=families.Binomial(), 
        cov_struct=sm.cov_struct.Exchangeable()
    )
    
    gee_results = model.fit()
    
    #print(gee_results.summary())


    gee_results_txt = gee_results_txt + running_title + str(gee_results.summary()) + "\n\n"
    #gee_results.params['const']
    #gee_results.params['side_numeric']
    #gee_results.pvalues['const']
    #gee_results.pvalues['side_numeric']
    
    # interpretation
    
    interp_txt = """The odds of an instance being “Individualized” are approximately {}% {} on the Palestine side than on the Israel side."""
    
    odds_ratio_side_numeric = np.exp(gee_results.params['side_numeric']).round(3)

    if odds_ratio_side_numeric < 1:
        temp_x = round((1-odds_ratio_side_numeric)*100,1)
        interp_txt = interp_txt.format(temp_x,'lower')
    
    else:
        temp_x = round((odds_ratio_side_numeric-1)*100,1)
        interp_txt = interp_txt.format(temp_x,'higher')
        
    gee_results_txt = gee_results_txt + interp_txt + "\n\n\n\n"

with open(output_file_name, 'w') as f:
    f.write(path_report + gee_results_txt) # Convert the Summary object to its string representation



# %% Fig 2A: Barplot

print("\nGenerating Fig 2A")


# 4x2 horiz bars showing the IG ratio per side per source
    
plot_font = 25

import seaborn as sns

b_width = 0.95


# Create the plot
fig_1, ax_1 = plt.subplots(figsize=(25, 8), dpi=600)

sns.barplot(a_T1_IG_Ratios, x="Indiv_to_Group_Ratio", y="Source", 
            hue="Side", 
            palette=dict_colors,
            #width = b_width,
            ax = ax_1,
            )

        
    
# Control axes labels
plt.xlabel('Individual Stories to Group Mentions Ratios', 
           fontweight='bold', 
           labelpad=20, fontsize=plot_font)

plt.ylabel('')

    
# Control axes ticks
plt.xticks(fontsize=plot_font-5)

plt.yticks(fontsize= 3)


# this code forces the x axis to show a tick value of 0.25
max_val = a_T1_IG_Ratios["Indiv_to_Group_Ratio"].max()
#ticks = np.arange(0, 1.01*max_val, 0.05)
ticks = np.arange(0, 0.26, 0.05)   
   
ax_1.set_xticks(ticks)

ax_1.set_xlim(0, 0.25)


# Adjust the legend
# -  remove side legend
ax_1.get_legend().remove()


# -  add a single unified legend for all subplots based on any subplot's data
handles, labels = ax_1.get_legend_handles_labels()
unique = dict(zip(labels, handles))
fig_1.legend(unique.values(), unique.keys(), bbox_to_anchor=(0.5, 0.9), loc='lower center', borderaxespad=0, ncol=2, fontsize=plot_font-5)


# Remove the plot boundaries
sns.despine()
    
# Export plot as svg to preserve resolution

title_i = 'Fig 2A - Ratio of Individualized to Grouped mentions per side for each media source.svg'
plt.savefig(path_report + title_i , format='svg',  bbox_inches='tight')

  

# %% ---------------------------
# %% Prompt 2: Hardship Label
# %% ---------------------------



# import the relevant columns only of the merged data

df_prompt_2 = df_hard_emp.copy()

df_prompt_2 = df_prompt_2.drop(['Vividness_of_Emotions','Plot_Volume'], axis=1)


# %% Count Hardship Sublabels

# Get count of hardship per side per source
df_hardship_simple = df_prompt_2.groupby(['Source','Side', 'Hardship'])['Instance_ID'].count().reset_index().sort_values(['Source','Side','Instance_ID'],ascending=[True, False, False])

df_hardship_simple = df_hardship_simple.rename(columns = {'Instance_ID':'Instance_Count'})

# export a copy for the past conflicts analysis
title_i = "IG_Prompt_2_Hardship_Label_Counts_Conflict_2023.csv"
df_hardship_simple.to_csv(path_past_conflict_agg_data + title_i)


# rearrange file
df_hardship = df_hardship_simple.pivot(index = ['Source', 'Side'], columns='Hardship', values='Instance_Count').fillna(0)

df_hardship = df_hardship.reset_index().sort_values(['Source','Side'],ascending=[True, False]).reset_index(drop=True).set_index(['Source','Side'])

df_hardship['Total'] = df_hardship.sum(axis=1)


    
# %% - Supp Fig 3: Barplots | Comparing Hardships

print("\nGenerating Supp Fig 3")

# 0. Switches

plot_font      = 25
bwidth         = 0.4

hardship_label =        [
                          'Casualties', 
                          'Imprisonment and Detention',
                          'Displacement and Refugees', 
                          'Vulnerable and Affected Groups',
                          'Missing',
                          'Deprivation, Malnutrition and Hunger',
                          'Health and Medical Conditions', 
                          'Humanitarian Aid and Dependence',
                          #'Other Hardship',
                         ]

consider_other = False


# 1. Data Preparation: Hardship Label Counts 

# -  create a copy for the plot to preserve the original dataset
a_T2_raw = df_hardship_simple.copy()


# -  limit the data to the selected hardships and label all else as "Other"
if len(hardship_label) > 0:
    
    a_T2_raw['Hardship'] = a_T2_raw['Hardship'].apply(lambda x: x if x in hardship_label else "Other")

    a_T2_raw = a_T2_raw.groupby(['Source','Side','Hardship'])['Instance_Count'].sum().reset_index()
    
    
fig_2_width = len(hardship_label)*2.25



# -  decide whether or not to plot the "Other" hardships
if consider_other == False:
    
    a_T2_raw = a_T2_raw[a_T2_raw['Hardship']!= 'Other'].copy()



# -  split the hardship labels over 2 lines
a_T2_raw['Hardship'] = a_T2_raw['Hardship'].apply(lambda x: x.replace(" and "," &_"))
a_T2_raw['Hardship'] = a_T2_raw['Hardship'].apply(lambda x: x.replace(" ","\n"))
a_T2_raw['Hardship'] = a_T2_raw['Hardship'].apply(lambda x: x.replace("_"," "))



# -  sort the data to preserve data order in the chart
a_T2_raw = a_T2_raw.sort_values(['Source','Side','Hardship'],
                                ascending = [True, False, True])



# Export a copy for the Past Conflicts Analysis
a_T2_raw_2023 = a_T2_raw.copy()
a_T2_raw_2023['Source'] = a_T2_raw_2023['Source'].apply(lambda x: dict_sources[x]) 
#a_T2_raw_2023.to_csv("11- Past Conflict Input Data/IG_Prompt_2_Hardship_Label_Counts_Conflict_2023.csv")





# 2. Data Preparation: Actual Casualty Counts

df_actual = pd.DataFrame({"Side": ['Palestine ', 'Israel '],
                          'Hardship': ['Actual\nCasualty\nCounts']*2,
                          'Instance_Count': [139700,6800]
                          })
    


# 3. Plot Data

fig_2, ax_2 = plt.subplots(4,1,figsize = (fig_2_width,20), sharex=True, sharey=True)            

for i, src_i in enumerate(sorted_sources):
            
    
    a_T2 = a_T2_raw[a_T2_raw['Source']==src_i].copy()


    
    # 4. Left-Plot a subplot for each source
    barplot_L = sns.barplot(a_T2, 
                            x="Hardship", 
                            y="Instance_Count", 
                            hue="Side", 
                            ax = ax_2[i], 
                            palette = dict_colors,
                            width = bwidth,
                            errorbar=None )

    # -  plot the count of instances over each bar
    barplot_L.bar_label(ax_2[i].containers[0], fontsize=plot_font-10, fontweight='bold')
    barplot_L.bar_label(ax_2[i].containers[1], fontsize=plot_font-10, fontweight='bold')
    
    
    
    # -  tweak the x and y axis tick parameters
    ax_2[i].tick_params(axis='x',labelsize = plot_font-10, labelrotation = 45)
    ax_2[i].tick_params(axis='y',labelsize = plot_font-7, labelrotation = 0)


    # -  remove the legends per each subplot 
    ax_2[i].get_legend().remove()
    
    
    # -  remove the y axis label from each subplot  
    ax_2[i].set_ylabel('')
    
    
    # -  add a title to each subplot
    ax_2[i].set_title(dict_sources[src_i], fontsize= plot_font-15 , fontweight='bold')
    
    
    # -  remove the top border of the plot
    sns.despine(ax = ax_2[i], top= True, right=True, left=False, bottom=False)


    
# 5. Modify the shared x axis label and ticks

# -  modify the last plot's x axis label 
ax_2[-1].set_xlabel('Individual Instance Hardship Label',  fontsize = plot_font, fontweight='bold', labelpad=20)


# -  modify the last plot's x axis ticks 
ax_2[-1].tick_params(axis='x', labelsize=plot_font-5)

for tick in ax_2[-1].get_xticklabels():
    tick.set_fontweight('bold')



# 6. Create a shared y axis label for all 4 subplots
# -  add a main Left y axis Label
y_axis_label = "Individualized Instance Count"
fig_2.text(0.065, 0.5, y_axis_label, va='center', rotation=90, fontsize = plot_font, fontweight='bold')
    


# 7. Add a single unified legend for all subplots based on any subplot's data

# Get left-axis handles/labels from the first subplot
left_handles, left_labels = ax_2[0].get_legend_handles_labels()
  
# Add unified legend
fig_2.legend(left_handles, left_labels,
     bbox_to_anchor=(0.5, 0.91), loc='lower center',
     borderaxespad=0, ncol=2, fontsize=plot_font - 5, frameon=False)



# 8. Export plot as svg to preserve resolution
title_i =  "Supp Fig 3 - Individualized instance counts by hardship category.svg"
plt.savefig(path_report + title_i , format='svg',  bbox_inches='tight')



# %% - Fig 2B: Barplots | Comparing Casualties

print("\nGenerating Fig 2B")

# 0. Switches

plot_font      = 20
bwidth         = 0.6
fig_x_width    = 18
fig_y_height   = 7
label_rot      = 0

hardship_label =        [
                          'Casualties', 
                          #'Imprisonment and Detention',
                          #'Displacement and Refugees', 
                          #'Vulnerable and Affected Groups',
                          #'Missing',
                          #'Deprivation, Malnutrition and Hunger',
                          #'Health and Medical Conditions', 
                          #'Humanitarian Aid and Dependence',
                          #'Other Hardship',
                         ]

consider_other = False



# 1. Data Preparation: Hardship Label Counts 

# -  create a copy for the plot to preserve the original dataset
a_T2_raw = df_hardship_simple.copy()

# -  limit the data to the selected hardships and label all else as "Other"
if len(hardship_label) > 0:
    
    a_T2_raw['Hardship'] = a_T2_raw['Hardship'].apply(lambda x: x if x in hardship_label else "Other")

    a_T2_raw = a_T2_raw.groupby(['Source','Side','Hardship'])['Instance_Count'].sum().reset_index()
    

# -  decide whether or not to plot the "Other" hardships
if consider_other == False:
    
    a_T2_raw = a_T2_raw[a_T2_raw['Hardship']!= 'Other'].copy()


# -  split the hardship labels over 2 lines
a_T2_raw['Hardship'] = a_T2_raw['Hardship'].apply(lambda x: x.replace(" and "," &_"))
a_T2_raw['Hardship'] = a_T2_raw['Hardship'].apply(lambda x: x.replace(" ","\n"))
a_T2_raw['Hardship'] = a_T2_raw['Hardship'].apply(lambda x: x.replace("_"," "))


# -  sort the data to preserve data order in the chart
a_T2_raw = a_T2_raw.sort_values(['Source','Side','Hardship'],
                                ascending = [True, False, True])


# -  replace source names with abbreviations        
a_T2_raw['Source'] = a_T2_raw['Source'].apply(lambda x: dict_sources[x])


# 2. Data Preparation: Actual Casualty Counts

df_actual = pd.DataFrame({"Side": ['Palestine ', 'Israel '],
                          'Hardship': ['Actual\nCasualty\nCounts']*2,
                          'Instance_Count': [139700,6800]
                          })
    

# 3. Plot Data

fig_2, ax_2 = plt.subplots(1,1,figsize = (fig_x_width,fig_y_height))            

for i, src_i in enumerate(sorted_sources):
            
    

    
    # 4. Left-Plot a subplot for each source
    barplot_L = sns.barplot(a_T2_raw, 
                            x="Source", 
                            y="Instance_Count", 
                            hue="Side", 
                            ax = ax_2, 
                            palette = dict_colors,
                            width = bwidth,
                            errorbar=None )


    # -  plot the count of instances over each bar
    barplot_L.bar_label(ax_2.containers[0], fontsize=plot_font-5, fontweight='bold', rotation=label_rot, padding= 10)
    barplot_L.bar_label(ax_2.containers[1], fontsize=plot_font-5, fontweight='bold', rotation=label_rot, padding= 10)
    
    
    # -  tweak the x and y axis tick parameters
    ax_2.tick_params(axis='x',labelsize = plot_font-2, labelrotation = 0)
    ax_2.tick_params(axis='y',labelsize = plot_font-7, labelrotation = label_rot)


    # -  remove the legends per each subplot 
    ax_2.get_legend().remove()
    
    
    # -  remove the y axis label from each subplot  
    ax_2.set_ylabel('')
    

    
    # -  remove the top border of the plot
    sns.despine(ax = ax_2, top= True, right=False, left=False, bottom=False)



    
    # 5. Right-Plot the actual casualty numbers
    
    # Define a main color for the bars, ticks and bar labels
    bar_R_color = '#CA2400'
    
    
    # Create right y-axis
    ax_2r = ax_2.twinx()


    # Plot right-axis bar with seaborn
    #sns.barplot(data=right_data, x='Hardship', y='value', color='red', ax=ax2)
    barplot_R = sns.barplot(df_actual, x = 'Hardship', y = 'Instance_Count', hue = 'Side', 
                palette = dict_colors, ax = ax_2r, width = bwidth*1)

    
    # -  plot the count of instances over each bar
    #barplot_R.bar_label(ax_2r.containers[0], fontsize=plot_font-5, color="#000000", fontweight='bold', rotation=0, padding= 10)
    barplot_R.bar_label(ax_2r.containers[-2], fontsize=plot_font-5, color=bar_R_color, fontweight='bold', rotation=0, padding= 10)
    barplot_R.bar_label(ax_2r.containers[-1], fontsize=plot_font-5, color=bar_R_color, fontweight='bold', rotation=0, padding= 10)

    
    # -  remove the y axis label and modify the axis params
    ax_2r.set_ylabel('')
    ax_2r.tick_params(axis='y', labelsize = plot_font-5, labelrotation = label_rot, labelcolor=bar_R_color)
    

    # -  remove the top border of the plot
    sns.despine(ax = ax_2r, top= True, right=False, left=False, bottom=False)
    
    
    # -  remove the legends per each subplot 
    ax_2r.get_legend().remove()

    
# 6. Modify the shared x axis label and ticks

# -  modify the last plot's x axis label 
#ax_2.set_xlabel('',  fontsize = plot_font, fontweight='bold', labelpad=20)

ax_2.set_xlabel('',  fontsize = plot_font, fontweight='bold', labelpad=20)


# -  modify the last plot's y axis label 
ax_2.set_ylabel('No. of Casualties Mentions',  fontsize = plot_font, fontweight='bold', labelpad=25)



# -  modify the last plot's x axis ticks 
ax_2.tick_params(axis='x', labelsize=plot_font-5)
ax_2.tick_params(axis='y', labelsize=plot_font-5)


for tick in ax_2.get_xticklabels():
    tick.set_fontweight('bold')



# 7. Create 2 shared y axis labels for all 4 subplots
# -  add a main Left y axis Label
#right_y_axis_label = "Individualized Instance Count"
#fig_2.text(-0.01, 0.5, right_y_axis_label, va='center', rotation=90, fontsize = plot_font, fontweight='bold')
    
# -  add a main Right x axis Label
left_y_axis_label = "Actual Casualty Counts in 1000s"
#fig_2.text(1.02, 0.5, left_y_axis_label, va='center', rotation=90, fontsize=plot_font, fontweight='bold', color= bar_R_color)
ax_2r.set_ylabel('Actual Casualty Counts in 1000s',  fontsize = plot_font, fontweight='bold', labelpad=25, color= bar_R_color)



# 8. Add a single unified legend for all subplots based on any subplot's data
#handles, labels = ax_2[0].get_legend_handles_labels()
#unique = dict(zip(labels, handles))
#fig_2.legend(unique.values(), unique.keys(), bbox_to_anchor=(0.5, 0.9), loc='lower center', borderaxespad=0, ncol=2, fontsize=plot_font-5)



# Get left-axis handles/labels from the first subplot
left_handles, left_labels = ax_2.get_legend_handles_labels()
right_handles, right_labels = ax_2r.get_legend_handles_labels()

  
# Combine: dynamic left + manual right
combined_handles = left_handles [:2] + right_handles
combined_labels  = left_labels  [:2] + right_labels

# Add unified legend
fig_2.legend(combined_handles, combined_labels,
     bbox_to_anchor=(0.51, 0.6), loc='lower center',
     borderaxespad=0, ncol=1, fontsize=plot_font - 5,
     )



# 9. Export plot as svg to preserve resolution
title_i =  "Fig 2B - Casualty Mentions vs Actual Casualties.svg"

plt.savefig(path_report + title_i , format='svg',  bbox_inches='tight')



# %% Count Oct 7 Label

# Overall Counts

# -  keep only Side = Isr
df_table_Oct7 = df_prompt_2[df_prompt_2['Side']=='Israel'].copy()


# -  keep only the 2 prominent Hardship labels
filter_Cas = df_table_Oct7['Hardship']=='Casualties'
filter_InD = df_table_Oct7['Hardship']=='Imprisonment and Detention'

df_table_Oct7 = df_table_Oct7[filter_Cas |  filter_InD] .copy()
   

# -  get counts of Oct 7 Label Instances
df_table_Oct7 = df_table_Oct7.groupby(['Source','Oct_7_Attack'])['Instance_ID'].count().reset_index()

df_table_Oct7 = df_table_Oct7.rename(columns = {'Instance_ID':'Instance_Counts'})


# -  get total counts of all instances per Source
temp_totals = df_table_Oct7.groupby('Source')['Instance_Counts'].sum().reset_index()

temp_totals = temp_totals.rename(columns = {'Instance_Counts':'Total_Israeli_Indualized_Stories'})


# -  merge the totals in 2 with the label counts from 1
df_table_Oct7 = df_table_Oct7.merge(temp_totals, on='Source')


# -  get Label Count % of Total Count
df_table_Oct7['Percent_of_Total'] = (100*df_table_Oct7['Instance_Counts']/df_table_Oct7['Total_Israeli_Indualized_Stories']).round(1)


# -  sort the table
df_table_Oct7 = df_table_Oct7[['Source', 'Total_Israeli_Indualized_Stories', 'Oct_7_Attack', 'Instance_Counts', 'Percent_of_Total']].copy()

a_T3_Oct_7 = df_table_Oct7.sort_values(['Source','Oct_7_Attack'], ascending = [True, False])


    

# Counts Grouped per Month

df_table_Oct7_month = df_prompt_2.copy()

df_table_Oct7_month['Oct_7_Attack_Bool'] = df_table_Oct7_month['Oct_7_Attack'].apply(lambda x: True if x=='Yes' else False)

df_table_Oct7_month = df_table_Oct7_month.groupby([pd.Grouper(key='Date', freq= "1MS"), 'Source'])['Oct_7_Attack_Bool'].sum().unstack().fillna(0).astype(int)

df_table_Oct7_month.columns = [dict_sources[i] for i in df_table_Oct7_month.columns]


a_T4_Oct_7_month = df_table_Oct7_month.reset_index().copy()

#a_T4_Oct_7_month['Date'] = a_T4_Oct_7_month['Date'].dt.strftime('%b %Y')

a_T4_Oct_7_month = a_T4_Oct_7_month.set_index('Date')




# % of Counts Grouped per Month

a_T4_Oct_7_month_percent = a_T4_Oct_7_month.copy()

a_T4_Oct_7_month_percent = round(100*a_T4_Oct_7_month_percent.div(a_T4_Oct_7_month_percent.sum(axis=0), axis=1),0).astype(int)
    
    
    
# %% - Fig 2C: Pie Chart

print("\nGenerating Fig 2C")


import matplotlib.pyplot as plt
import seaborn as sns

# Switches
side_pie = 'Israel'

plot_font      = 20
margin_i       = 10
hardship_label =        [
                          'Casualties', 
                          #'Imprisonment and Detention',
                          #'Displacement and Refugees', 
                          #'Vulnerable and Affected Groups',
                          #'Missing',
                          #'Deprivation, Malnutrition and Hunger',
                          #'Health and Medical Conditions', 
                          #'Humanitarian Aid and Dependence',
                          #'Other Hardship',
                         ]


# Data Preparation


# -  keep only Side = Isr
df_o7_pie= df_prompt_2[df_prompt_2['Side']== 'Israel'].copy()


# -  keep only instances of the following hardship labels
if len(hardship_label) > 0:
    df_o7_pie = df_o7_pie[df_o7_pie['Hardship'].isin(hardship_label)]
    

# -  exclude AJE
df_o7_pie = df_o7_pie[df_o7_pie['Source']!='Al Jazeera English'].copy()


# -   get group counts
df_o7_pie_grp = df_o7_pie.groupby(['Oct_7_Attack'])['Instance_ID'].count().reset_index()
df_o7_pie_grp = df_o7_pie_grp.rename(columns = {'Instance_ID':'Instance_Count'})


# Data Plotting - Pie Chart

df_p2_oct_pie = df_o7_pie_grp['Instance_Count'].to_list()
labels = df_o7_pie_grp['Oct_7_Attack'].to_list()

colors = ['#fcbf49', dict_colors['Oct_7_Label']]
#['#fcbf49','#d62828']
fig_3, ax_3 = plt.subplots(dpi = 600)

wedges, texts, autotexts = ax_3.pie(
    df_p2_oct_pie,
    labels=labels,
    colors=colors,
    startangle=90,
    autopct='%.0f%%',
    wedgeprops=dict(width=0.5),
    pctdistance=0.75,    # move percent labels outward
    labeldistance=1.2   # move category labels outward
)

# Add text in center
ax_3.text(0, 0, side_pie+'\nCasualty\nStories', ha='center', va='center', fontsize=plot_font-6, fontweight='bold')

# Customize the label texts (outside pie)
for label in texts:
    label.set_color('black')      # e.g. black or any other color
    label.set_fontsize(plot_font-5)        # bigger font size
    label.set_fontweight('bold')
    
# Customize the percentage texts (inside pie)
for pct in autotexts:
    pct.set_color('white')     # stand out against wedge color
    pct.set_fontsize(plot_font)       # larger number font
    #pct.set_fontweight('bold')
    

# Export the chart
title_i = "Fig 2C - Proportion of Western media’s Israeli casualty stories mentioning Oct 7 or hostages.svg"
plt.savefig(path_report + title_i , format='svg',  bbox_inches='tight')
    
    
            
            
# %% Supp Fig 4
    
print("\nGenerating Supp Fig 4")


# 0. Specify counts to analyze
analyze_counts = 'Deaths' 
oct_7_stories  = True
apply_decay    = False


# 1. Import and group events
df_events = pd.read_excel(path_critical_events, sheet_name='Final_List')

df_events['Date'] = pd.to_datetime(df_events['Date'], format = "%Y-%m-%d")

# -  this removes the Oct 7 attack event
df_events = df_events.dropna(subset = [analyze_counts]).copy()



# 2. Filter by Side and Decay period

df_critical_events = df_events [ df_events['Affected']   == 'Palestine' ].copy()

if apply_decay == True:
    
    start_date = '2023-12-01'
    end_date   = '2024-09-10' 
    
    filter_decay = (df_critical_events['Date'] >= start_date) & (df_critical_events['Date'] <= end_date)
    
    df_critical_events = df_critical_events[filter_decay].copy()
    
 


# 3. Get counts of Dead civilians on event days

df_critical_casualties = df_critical_events.copy()

df_critical_casualties[analyze_counts] = df_critical_casualties[analyze_counts].astype(int)

df_critical_casualties = df_critical_casualties[['Date', 
                                                 'Caption', 
                                                  analyze_counts, 
                                                 'Source List', 
                                                 'Affected']].copy()

df_critical_casualties = df_critical_casualties.groupby(['Date'])[analyze_counts].sum().reset_index()




# 4. Get the list of critical days (event day and the day after)
critical_days = pd.concat([df_critical_casualties['Date'], 
                          (df_critical_casualties['Date']+ timedelta(days=1))])

critical_days = critical_days.sort_values().to_frame()




# 5. Get the num of Isr stories on critical days (event day + day after)

df_hard_emp_mod = df_hard_emp.copy()

#df_hard_emp_mod = df_hard_emp[df_hard_emp['Hardship']=='Casualties'].copy()


# -  apply filter to limit stories with Oct 7 flag or not
if oct_7_stories == True:
    
    df_hard_emp_mod = df_hard_emp_mod[df_hard_emp_mod['Oct_7_Attack']=='Yes'].copy()

    
    
# -  get the number of Isr stories per all days 

df_isr_stories = df_hard_emp_mod.groupby(['Date','Side'])['Instance_ID'].count().reset_index()

df_isr_stories = df_isr_stories.rename(columns = {'Instance_ID':'Story_Count'})    

df_isr_stories = df_isr_stories[df_isr_stories['Side']=='Israel'].copy()

df_isr_stories = df_isr_stories.drop(['Side'], axis=1)


# -  filter data above to get the number of Isr stories per critical days 
#    (event day + day after)

df_critical_stories = critical_days.merge(df_isr_stories, on='Date', how='left').fillna(0)

temp_sum = df_critical_stories.loc[::2, 'Story_Count'].reset_index(drop=True)+df_critical_stories.loc[1::2, 'Story_Count'].reset_index(drop=True)

df_critical_stories = pd.DataFrame({'Date'       : df_critical_stories.loc[::2, 'Date'],
                                    'Story_Count': temp_sum.values})




# 6. Merge the datasets -> Num of Pal Casualties vs Num of Isr Stories

df_pal_cal_isr_story = df_critical_casualties.merge(df_critical_stories, on='Date', how='left')    
df_pal_cal_isr_story['Story_Count'] = df_pal_cal_isr_story['Story_Count'] .astype(int)



# 7. Remove Outliers - points with stories more than 100

# -  this removes 2 points (09 Oct 2023 and 06 Oct 2024 - both make sense)
df_pal_cal_isr_story = df_pal_cal_isr_story[df_pal_cal_isr_story['Story_Count']<100].copy()


df_pal_cal_isr_story = df_pal_cal_isr_story.reset_index(drop=True)




# 8. Calculate & Plot Correlation

from scipy.stats import pearsonr, spearmanr


# -  identify the two variables
x = df_pal_cal_isr_story[analyze_counts]
y = df_pal_cal_isr_story['Story_Count']


# -  calculate Pearson correlation
pearson_corr, p_val = pearsonr(x, y)
print("Pearson correlation:", round(pearson_corr,2), "p-value:", round(p_val,3))

# -  calculate Spearman correlation
spearman_corr, p_val_spear = spearmanr(x, y)
print("Spearman correlation:", round(spearman_corr,2), "p-value:", round(p_val_spear,3))



# -  code to plot the scatterplot of Pal Casualties vs Isr Stories
fig, ax = plt.subplots(figsize=(8,6))

sns.scatterplot(x = analyze_counts, 
                     y = 'Story_Count', 
                     data = df_pal_cal_isr_story,
                     palette="tab20",
                     hue = analyze_counts,
                     legend = False,
                     ax = ax
                     )


ax = sns.regplot(x=analyze_counts,  
                 y='Story_Count', 
                 data=df_pal_cal_isr_story, 
                 ci=95, 
                 scatter = False,
                 scatter_kws={"color": "blue", "s": 20},
                 line_kws={"color":"black", "linewidth":1},
                 ax = ax
                 )


# -  write text on plot - pearson and Significance
text_on_plot = "r = "+ str(round(pearson_corr,2)) + ", p = " + str(round(p_val,3))

ax.text(10, 80, text_on_plot, fontsize=12, fontstyle='italic')


# -  beautify the plot
ax.set_xlabel("Num of Palestinian " + analyze_counts, fontweight='bold', fontsize = 12, labelpad=15)

y_axis_label = "Num of Israeli Stories"

if oct_7_stories == True:
    
    y_axis_label = y_axis_label + " Related to Oct 7 Attack"

ax.set_ylabel(y_axis_label, fontweight='bold', fontsize = 12, labelpad=15)


ax.set_xticks(np.linspace(0, 
                          round(df_pal_cal_isr_story[analyze_counts].max(),-2), 
                          num=11))

ax.set_yticks(np.linspace(0, 90,  num=10))


# -  export plot as svg to preserve resolution
title_i = "Supp Fig 4 - Correlation between Palestinian civilian deaths and Israeli story coverage.svg"
plt.savefig(path_report + title_i , format='svg',  bbox_inches='tight')





# %% Supp Tab 4

print("\nGenerating Supp Tab 4")

# Note: it is important to take into account the time difference between the 
#       East and the West. Gaza and CNN have a time difference for example of
#       around 6-7 hours.

# Concurrent Reporting - Counts of Oct 7 Stories out of Total Pal and Isr per Day


# 0. Specify whether to inspect counts of all stories or Oct-7 ones only

story_col_counts =    'Oct_7_Pal_Stories_Count' # All_Stories_Count, Oct_7_Pal_Stories_Count


# 1. Specify dates and Stories to inspect

inspect_dates_0 = pd.Series(pd.to_datetime([
                                '2023-12-01',
                                '2024-02-29',
                                '2024-09-10',
                                
                                '2024-01-15',
                                '2024-06-08',
                                '2024-09-01',
                                ]))

inspect_dates = pd.concat([inspect_dates_0, inspect_dates_0 + timedelta(days=1)]).reset_index(drop=True)



# 2. Prepare dataset

# -  filter data by date
df_hard_emp_ltd = df_hard_emp[(df_hard_emp['Date'].isin(inspect_dates))].copy()


# -  convert the Oct 7 [yes no] labels to [1 and 0] for counting purposes
df_hard_emp_ltd['Oct_7_Attack'] = df_hard_emp_ltd['Oct_7_Attack'].apply(lambda x: 1 if x=='Yes' else 0)




# 3. Count Israeli Oct 7 Individualized Instances (stories)

# - get counts of Oct 7 stories per source per day
o7_counts = df_hard_emp_ltd.groupby(['Date','Source','Side'])['Oct_7_Attack'].sum().reset_index()

o7_counts = o7_counts.rename(columns={'Oct_7_Attack':'Oct_7_Stories_Count'})

# -  exclude non-western media sources and count only Israeli Oct 7 stories
o7_counts = o7_counts[(o7_counts['Source']!='Al Jazeera English') & (o7_counts['Side']=='Israel')].copy()




# 4. Count all stories per side per day
stories_counts = df_hard_emp_ltd.groupby(['Date','Source','Side'])['Instance_ID'].count().reset_index()

stories_counts = stories_counts.rename(columns={'Instance_ID':'All_Stories_Count'})

stories_counts = stories_counts[(stories_counts['Source']!='Al Jazeera English')]



# 5. Merge datasets
a_concurrent_rep = stories_counts.merge(o7_counts, on = ['Date','Source', 'Side'],how='outer').fillna(0)

a_concurrent_rep['Oct_7_Stories_Count'] = a_concurrent_rep['Oct_7_Stories_Count'].astype(int)



# 6. Create a new column to incorporate both Pal story counts and 
#    Israel's Oct 7 (only) story counts

a_concurrent_rep['Oct_7_Pal_Stories_Count'] = a_concurrent_rep.apply(lambda x: x['Oct_7_Stories_Count'] if x['Side']=='Israel' else x['All_Stories_Count'], axis=1)




# 7. Postprocess dataset

a_concurrent_rep['Source'] =  a_concurrent_rep['Source'].apply(lambda x: dict_sources[x])
                

a_concurrent_rep = a_concurrent_rep.sort_values(['Source','Side'], ascending = [True, False])


a_concurrent_rep = a_concurrent_rep.pivot(index   ='Date', 
                                          columns = ['Source','Side'], 
                                          values  = [story_col_counts],
                                          ).fillna(0)


# Rearrange Table
df_supp_tab_4 = a_concurrent_rep.groupby(np.arange(len(a_concurrent_rep)) // 2).sum()
df_supp_tab_4.index = a_concurrent_rep.index[::2]
df_supp_tab_4 = df_supp_tab_4.loc[inspect_dates_0]


# Export
title_i = 'Supp Tab 4 - Count of Western Media’s Individualized Hardshiprelated Stories per Side per Source for selected major events.svg'
df_supp_tab_4.to_csv(path_report + title_i + '.csv')



# %% ---------------------------
# %% Empathy Analyses
# %% ---------------------------

if analyze_prompt_empathy == True:
        
    # %% Switches
    
    run_empathy_analyses    = [
                                'Vividness_of_Emotions', 
                                'Plot_Volume',
                                ]
    
    hardship_label =        [
                              #'Casualties', 
                              #'Imprisonment and Detention',
                              #'Displacement and Refugees', 
                              #'Vulnerable and Affected Groups',
                              #'Missing',
                              #'Deprivation, Malnutrition and Hunger',
                              #'Health and Medical Conditions', 
                              #'Humanitarian Aid and Dependence',
                              #'Other Hardship',
                             ]
    

    aggregation_fn           = 'sum'  # sum, mean
    
    plot_weekly_mean         = True
    
    include_0_story_articles = True
    
    gen_empathy_events_table = False
                    
    smoothing_res            = 10000 #10000
    
    plot_group_freq          = "6D"   # 6D, 4MS
    
    investigate_peaks        = False
    
    dpi = 300
    
    fig_time_x               = 60
    
    yaxis_limits             = [-5,2] # [min, max] [-60,50]
    
    plot_format              = 'svg' #svg


    if plot_weekly_mean == True:
        plot_weekly_title = 'weekly mean'
    else:
        plot_weekly_title = 'weekly sum'


    # Create an overall empty backbone dataset to hold all empathy analysis

    a_T7_empathy_mean_rating = pd.DataFrame({'Source':sorted_sources})
    

    # Create a for loop that extracts the selected empathy metric data and 
    # calculates the overall average tables and timeline plots
    
    for empathy_analysis in run_empathy_analyses:
        
            
        # %% Calc Mean Diff Rating / Article
        
        print("\n   ",empathy_analysis)
        
        
        # 1. Import Empathy Data
        
        keep_cols = ['Instance_ID', 'Hardship', 'Entity', 'Phrases', 
                     'Article_ID', 'Source', 'Location', 'Date', 
                     'Side', 'Civilian_Status'] + [empathy_analysis]
        
        df_empathy_rating = df_hard_emp[keep_cols].copy()
        
    
        # -  keep only those articles with a specific hardship label(s)
        
        if len(hardship_label)>0:
            
            # Filter by hardship labels
            hardship_filter = df_empathy_rating['Hardship'].isin(hardship_label)
            
            df_empathy_rating = df_empathy_rating[hardship_filter].copy()
             
            
            
            
        # 2. Aggregate the Rating column per Side per Article
        group_cols = ['Date','Source','Article_ID','Side']
        
        if aggregation_fn == 'sum':
            agg_rating_col = df_empathy_rating.groupby(group_cols)[empathy_analysis].sum()
        
        
        if aggregation_fn == 'mean':
            agg_rating_col = df_empathy_rating.groupby(group_cols)[empathy_analysis].mean()
        

        agg_rating_col = agg_rating_col.rename('Agg_Rating')
        
        
        
        
        # 3. Backbone data
        #    Create an EMPTY SHELL dataset that holds all combinations of 
        #    dates, article ids, Sources and Sides
        
        article_ids = df_primary[['Date', 'Source','Article_ID']].drop_duplicates().copy()
            
        article_sides = pd.DataFrame({'Side' : ['Palestine','Israel']})
        
        df_src_side_id = article_ids.merge(article_sides, how='cross')
    
    
    
    
        # 4. Merge dataset from 2 on the backbone dataset from 0
        #    [Source, Article_ID, Side, Aggregated Rating]
        
        merge_how = "left" if include_0_story_articles == True else "inner"
        
        df_src_side_id_agg_rating = df_src_side_id.merge(agg_rating_col, on=group_cols, how= merge_how).fillna(0)
            
    
        

        # 5. Pivot the data to make it easier to get the difference between the 2 sides
        #    [Source, Article_ID, Pal_diff_Isr_Agg_Metric]
        
        df_src_side_id_rating_diff = df_src_side_id_agg_rating.pivot(index=['Date', 'Source','Article_ID'], columns='Side', values='Agg_Rating').fillna(0)
        
        df_src_side_id_rating_diff['Pal_diff_Isr_Agg_Metric'] = df_src_side_id_rating_diff['Palestine'] - df_src_side_id_rating_diff['Israel'] 

        df_src_side_id_rating_diff = df_src_side_id_rating_diff.reset_index()[['Date','Source', 'Article_ID','Pal_diff_Isr_Agg_Metric']].copy()
        


        
        # 6. Export table to show the overall mean differential rating per Source 

        df_src_side_id_rating_diff_mean = df_src_side_id_rating_diff.groupby(['Source'])['Pal_diff_Isr_Agg_Metric'].mean().round(1).reset_index()
    
        df_src_side_id_rating_diff_mean.columns = ['Source', 'Mean Rating: '+empathy_analysis]
        
        a_T7_empathy_mean_rating = a_T7_empathy_mean_rating.merge(df_src_side_id_rating_diff_mean, on='Source', how = 'left')
        

            
    
        
        # %% Hardship Label Counts / Article
        #    Pal: +ve, Isr: -ve
        group_cols = ['Date','Source','Side','Article_ID']
        
        # 1. Get Hardship Label Counts per Side per Article 
        df_src_side_art_hard = df_hard_emp[['Date','Source','Side', 'Article_ID', 'Instance_ID', 'Hardship']].copy()

        df_src_side_art_hard = df_src_side_art_hard.groupby(group_cols + ['Hardship'])['Instance_ID'].count().reset_index()
        
        df_src_side_art_hard = df_src_side_art_hard.rename(columns = {'Instance_ID':'Hardship_Count'})
        
        df_src_side_art_hard = df_src_side_art_hard.pivot(index = group_cols, columns = 'Hardship', values = 'Hardship_Count').fillna(0).reset_index()



        # 2. Backbone data
        #    Create an EMPTY SHELL dataset that holds all combinations of dates,
        #    article ids, Sources and Sides
        
        article_ids = df_primary[['Date', 'Source','Article_ID']].drop_duplicates().copy()
            
        article_sides = pd.DataFrame({'Side' : ['Palestine','Israel']})
        
        df_src_side_id = article_ids.merge(article_sides, how='cross')
        
        df_src_side_id = df_src_side_id.sort_values(['Date','Source','Article_ID','Side']).copy()
                
        
                
        # 3. Merge 1 and 2
    
        df_src_side_art_hard_all = df_src_side_id.merge(df_src_side_art_hard, how='left').fillna(0)



        # 4. Subtract both Side counts
        
        # -  create a dataset with pal counts
        
        temp_pal = df_src_side_art_hard_all[df_src_side_art_hard_all['Side']=='Palestine']
        temp_pal = temp_pal.drop(['Side'], axis = 1)
        temp_pal = temp_pal.set_index(['Date', 'Source','Article_ID'])
        
        # -  create a dataset with isr counts

        temp_isr = df_src_side_art_hard_all[df_src_side_art_hard_all['Side']=='Israel']
        temp_isr = temp_isr.drop(['Side'], axis = 1)
        temp_isr = temp_isr.set_index(['Date', 'Source','Article_ID'])

        # -  subtract both
        df_src_side_art_hard_all_diff = (temp_pal - temp_isr).reset_index()
        

        
    
        # %% Empathy Hardship Events
        
        # 1. Get Mean Diff Rating per Source every N Period (NP)
        if plot_weekly_mean == True:
            df_np_src_mean_rating_stacked = df_src_side_id_rating_diff.groupby([pd.Grouper(key='Date', freq = plot_group_freq), 'Source'])['Pal_diff_Isr_Agg_Metric'].mean()
        
        else:
            df_np_src_mean_rating_stacked = df_src_side_id_rating_diff.groupby([pd.Grouper(key='Date', freq = plot_group_freq), 'Source'])['Pal_diff_Isr_Agg_Metric'].sum()
        
        df_np_src_mean_rating = df_np_src_mean_rating_stacked.reset_index().copy()


        # 2. Get Sum of hardship counts every N Period  (NP)
        hard_labels = list(temp_pal.columns)

        df_np_src_sum_hard = df_src_side_art_hard_all_diff.groupby([pd.Grouper(key='Date', freq = '6D'), 'Source'])[hard_labels].sum().reset_index()



        # 3. Import and group event captions
        df_events = pd.read_excel(path_critical_events, sheet_name='Final_List')

        df_events['Date'] = pd.to_datetime(df_events['Date'], format = "%Y-%m-%d")
        
        df_np_events = df_events.groupby([pd.Grouper(key='Date', 
                                                         freq = plot_group_freq)])['Caption'].apply(list).reset_index()

        df_np_events = df_np_events.rename(columns = {'Caption':'Events'})
        
        
        
        # 4. Merge Rating, Hardship Counts and Event Captions datasets
        
        # -  hardship with rating
        df_np_rating_hard = df_np_src_sum_hard.merge(df_np_src_mean_rating)
        
        # -  hardship+rating with events
        df_np_rating_hard_events = df_np_rating_hard.merge(df_np_events, how='left')
        


        # 5. Prettify dataset
        df_np_rating_hard_events['Pal_diff_Isr_Agg_Metric'] = df_np_rating_hard_events['Pal_diff_Isr_Agg_Metric'].round(2)
        
        df_np_rating_hard_events['Date']    = df_np_rating_hard_events['Date'].dt.strftime('%d %b %Y')

        df_np_rating_hard_events['Source']  = df_np_rating_hard_events['Source'].apply(lambda x: dict_sources[x])
        
        df_np_rating_hard_events['Events'] = df_np_rating_hard_events['Events'].drop_duplicates()
        
        
        a_T7_hard_emp_events_weekly = df_np_rating_hard_events.fillna('').copy()
        
        
        
        # %% - Fig 2D + Supp Fig 5: Time Line Plots
        
        print("\nGenerating Fig 2D")
        print("\nGenerating Supp Fig 5")


        # 7. Draw a timeline for the diff in rating per article grouped per 
        #    6 days per side per source
        
        if analyze_prompt_empathy_time == True:
            
            # Set the title to which the plot will be saved

            # Specific plot parameters - improves scale
            if empathy_analysis == 'Vividness_of_Emotions':
                
                fig_time_y               = 40 
                
                yaxis_limits             = [-5,2]
                
                title_i = "Fig 2D - Weekly avg diff in {} scores per Source - 12 months.svg"
                title_i = title_i.format(empathy_analysis)

                
                
            elif empathy_analysis == 'Plot_Volume':
                
                fig_time_y               = 60 
                
                yaxis_limits             = [-9,2]
                
                title_i = "Supp Fig 5 - Weekly avg diff in {} scores per Source - 12 months.svg"
                title_i = title_i.format(empathy_analysis)
                
                
            # -  group the ratings per every plot_group_freq period
            #df_plot = df_src_side_id_rating_diff.groupby([pd.Grouper(key='Date', freq = plot_group_freq), 'Source'])['Pal_diff_Isr_Agg_Metric'].mean().unstack().fillna(0)
            df_plot = df_np_src_mean_rating_stacked.unstack().fillna(0)
            
            # -  export as excel
            df_plot_exp = df_plot.reset_index().copy()
            
            df_plot_exp['Date'] = df_plot_exp['Date'].dt.strftime('%d %B %Y')
                


            # - smooth the data
            if smoothing_res > 0:
                
                df_plot = smooth_plot(df_plot, res = smoothing_res)  # 10000
        
            
        
            # - seaborn timeline code
            import seaborn as sns
        
            fig_4, ax_4 = plt.subplots(4,1,figsize = (fig_time_x,fig_time_y), sharey=True, sharex = True)
        
            plot_font    = 52
        
        
            for i, src_i in enumerate(sorted_sources):
                                    
                df_plot_i = df_plot[src_i].copy()
                
                df_background = df_plot_i.reset_index().copy()

                df_background.columns = ['Date', src_i]

                sns.set_theme(rc={"figure.dpi": dpi})
        
                sns.set_style("whitegrid", {'axes.grid' : False})
        
                plot_i = sns.lineplot(
                             data=df_plot_i.to_frame(),
                             dashes=False,
                             legend = False,
                             ax = ax_4[i]
                            )
                
                if yaxis_limits!= []:
                    ax_4[i].set_ylim(yaxis_limits[0],yaxis_limits[1])
                
                # - remove plot boundaries (top and right)
                #sns.despine()
                
                
                # -  fill with Green where the curve is above x axis
                ax_4[i].fill_between(df_background['Date'], df_background[src_i], 0, 
                                where=(df_background[src_i] >= 0), interpolate=True, 
                                color=dict_colors['Palestine'], alpha=0.3)
    
    
                # -  fill with Blue where the curve is below x axis
                ax_4[i].fill_between(df_background['Date'], df_background[src_i], 0, 
                                where=(df_background[src_i] < 0), interpolate=True, 
                                color=dict_colors['Israel'], alpha=0.3)
    
    
    
                # -  plot a horizontal line to show the x-axis
                ax_4[i].axhline(0)
                
                
                # - add text annotations to flag the lowest rating dates
                low_ratings = df_plot_exp[['Date',src_i]].sort_values([src_i]).head()
                
                low_ratings = low_ratings[low_ratings['Date']!= '07 October 2023'].copy()
                
                low_ratings = low_ratings[low_ratings[src_i]< -1].copy()

                low_ratings['Date'] = pd.to_datetime(low_ratings['Date'], 
                                                     format = "%d %B %Y")
                
                """
                for low_rating_date,val in zip(low_ratings['Date'],low_ratings[src_i]):
                    ax_4[i].axvline(low_rating_date, color='red', 
                                   linestyle='--', linewidth=2, ymax = 0,
                                   )
                    
                    ax_4[i].text(low_rating_date, # x_coord
                            yaxis_limits[0], # y_coord
                            #low_rating_date.strftime("%d %b"), # text to display
                            'x',# text to display
                            fontsize=plot_font-10, 
                            color='red',
                            horizontalalignment='center', 
                            verticalalignment='bottom',
                            rotation = 90
                            )
                """
                
                # -  update the title of each of the subplots to show the name of the source
                plot_i.set_title(dict_sources[src_i], fontsize = plot_font, y=1.01, fontweight='bold')
        
        
                # -  remove x and y axis labels
                plot_i.set_xlabel('', fontsize = 4)
                plot_i.set_ylabel('', fontsize = plot_font)
        
        
                # -  update label ticks font size
                ax_4[i].tick_params(axis='x',labelsize = plot_font, labelrotation = 45, 
                                   #pad = 100
                                   )
                ax_4[i].tick_params(axis='y',labelsize = plot_font, labelrotation = 0)
        
                
                # -  create a main yaxis label for the 4 plots
                y_axis_label = "Weekly " + empathy_analysis.replace("_"," ") + " Difference Score (Palestinian - Israeli)"
                
                fig_4.supylabel(y_axis_label, fontsize = plot_font+10, fontweight='bold', y=0.5, x=-0.01)
        
        
                # -  update the x axis to properly display the dates
                ax_4[i].xaxis.set_major_locator(mdates.MonthLocator())
                ax_4[i].xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
                
                
                #ax_4[i].xaxis.set_major_locator(mdates.DayLocator(interval=6))
                #ax_4[i].xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        
            
                # -  tighten the plot layout and export
                plt.tight_layout()
        
                # -  export the plot as pdf
                plt.savefig(path_report + title_i, bbox_inches="tight", pad_inches=0.3, dpi=300)
        


# %% ---------------------------
# %% Prompt 3 - Children Label Counts
# %% ---------------------------

#%% Supp Tab 5

print("\nGenerating Supp Tab 5")


# %% - Filter & Clean Data

# -  keep only instances with child references

filter_child = df_child_raw['Is_Child']!='N_A'
df_child     = df_child_raw[filter_child].copy()


# -  keep only instances with Gaza Israel location references

filter_loc = df_child['Location'].isin(['Gaza', 'Israel'])
df_child     = df_child[filter_loc].copy()



# %% Count Child Label

T8_child_counts = df_child.groupby(['Source','Side','Type'])['Is_Child'].count().reset_index()

T8_child_counts = T8_child_counts.rename(columns = {'Is_Child':'Children_References'})

T8_child_counts = T8_child_counts.sort_values(['Source','Side', 'Type'], ascending = [True, False,False])

T8_child_counts['Source'] = T8_child_counts['Source'].apply(lambda x: dict_sources[x])


a_T8_child_counts = T8_child_counts.reset_index(drop=True).copy() 

a_T8_child_counts = a_T8_child_counts.pivot(index=['Source', 'Side'], columns = ['Type'], values=['Children_References']).reset_index()
a_T8_child_counts = a_T8_child_counts.sort_values(['Source','Side'], ascending = [True, False])


df_supp_tab_5 = a_T8_child_counts.copy()

df_supp_tab_5.columns = ['Source', 'Side', 'Grouped', 'Individualized']

df_temp = df_indiv.groupby(['Source','Side'])['Article_ID'].count().reset_index(name='Total')

df_temp['Source'] = df_temp['Source'].apply(lambda x: dict_sources[x])

df_supp_tab_5 =  df_supp_tab_5.merge(df_temp,
                                         on  = ['Source','Side'],
                                         how = 'left')

df_supp_tab_5 = df_supp_tab_5.drop(['Grouped'], axis=1)

df_supp_tab_5 = df_supp_tab_5.rename(columns = {"Individualized":"Child-related"})

df_supp_tab_5['Percent Child-related'] = (100* df_supp_tab_5['Child-related']/df_supp_tab_5['Total']).round(0)
# Export
title_i = "Supp Tab 5 - Child-related Individualized Stories.csv"
   
df_supp_tab_5.to_csv(path_report + title_i)
