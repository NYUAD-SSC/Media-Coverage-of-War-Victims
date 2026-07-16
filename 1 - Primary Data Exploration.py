#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The code below generates the following list of figures:

Fig 1: Total Number of Relevant Articles per News Source.

       It is divided into the following subplots:
           
        Fig 1A: The bar plot shows the overall count of relevant articles per each 
                of the four media sources. 
                
        Fig 1B: the timeline plot below shows the same number of articles but 
                spread out over time along with major war events that affected 
                Palestinian and Israeli sides displayed in green and blue 
                respectively. Both plots cover the first 12 months of the conflict.
            
    
"""

# %% Libraries
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import interpolate
from datetime import timedelta 
import matplotlib.dates as mdates


# %% Dictionaries

# Use the Dict to plot the Source Acronyms instead of the fullname

src_dict = {
            "Al Jazeera English":"AJE",
            "BBC":"BBC",
            "CNN Wire": "CNN",
            "The New York Times":"NYT"
            }


# %% Global Plot Parameters

dpi = 300
sns.set_theme(rc={"figure.dpi": dpi})
sns.set_style("whitegrid", {'axes.grid' : False})
sns.set_color_codes("pastel")


figsize_x       = 40
figsize_y       = 60
main_plot_font  = 40


# %% Paths

path_primary_data    = "01- Primary Data/df_primary.csv"

path_plot_colors     = "02- Secondary Data/02- Project Plotting Colors.xlsx"

path_critical_events = "02- Secondary Data/03- Conflict Events.xlsx"

analysis_output      = '05- Report Plots and Tables/'



# %% ----------------------------------

# %% Import Data

print("\nImport data...")

# Project Plotting Colors
color_dict = pd.read_excel(path_plot_colors, usecols = ["Entity","Color"])

color_dict = color_dict.dropna().set_index('Entity')['Color'].to_dict()


# Primary Data
df_primary = pd.read_csv(path_primary_data)

if "Unnamed: 0" in df_primary.columns:
    df_primary = df_primary.drop(["Unnamed: 0"], axis=1)


df_primary['Date'] = pd.to_datetime(df_primary['Date'], format = "%d %B %Y")



# %% Fig 1A: Barplot - Total Article Count

print("\n   Generating Fig 1A")


# [1] Prepare Plotting Data

# - sort the data so that the sources are alphabetically ordered in the legend
df_fig_1a = df_primary.sort_values("Source", ascending = True).copy()


# - replace the source names with their abbreviations
df_fig_1a['Source'] = df_fig_1a['Source'].apply(lambda x: src_dict[x])


# - add a dummy column to count instances
df_fig_1a['inst_count'] = 1



# [2] Plot the Barplot using data from 1

fig1, ax1 = plt.subplots(2,1,
                         figsize=(figsize_x, 
                                  figsize_y-5),
                         height_ratios=[1.5,3])


sns.barplot(data      = df_fig_1a,
            x         = "inst_count",
            y         = "Source",
            estimator = 'sum',
            ax        = ax1[0],
            hue       = "Source",
            width     = 0.4,
            palette   = color_dict)


# [3] Tweak the plot 

# - add labels to represent counts for each bar
for container, bar_color in zip(ax1[0].containers,df_fig_1a['Source'].unique()):

    ax1[0].bar_label(container, color = color_dict[bar_color], padding=15, fontsize=main_plot_font)


# -  further axes tweaks
sns.despine()

ax1[0].set(ylabel=None)

ax1[0].set_xlabel("Number of Articles", fontsize=main_plot_font, fontweight='bold', labelpad = 10 )

ax1[0].tick_params(axis='x', which='major', labelsize=main_plot_font)




# %% Fig 1B: Timeline - Weekly Article Counts Per Source

print("\n   Generating Fig 1B")


# [1] Preprocess Data - Calculate Count of Weekly Published Articles per Source 

total_art = pd.DataFrame({'Date':df_primary['Date'].unique()})

for src in df_primary['Source'].unique():

    temp_df = df_primary[df_primary['Source']==src]
    temp_df = temp_df.groupby([pd.Grouper(key='Date', freq='6D')])['Article_ID'].count()
    temp_df = temp_df.reset_index()
    temp_df.columns = ['Date', src]
    total_art = total_art.merge(temp_df, on = 'Date', how='outer')

total_art = total_art.set_index('Date')




# [2] Function takes in the date-indexed data and produces a timeline plot

def plot_multiple_lines(data, x_label='', y_label='', title = 'Title',
                        res_dpi = dpi, fig_x=10, fig_y=17,
                        fig_axes_defined = False, ax_i='',
                        plot_vline = True, plot_legend = True,
                        plot_fonts = 26,
                        pal_label_ratio = 1.1,
                        pad_plot = 1,
                        bias_plot = False,
                        set_y_lim = False,
                        v_label_max_manual = 1,
                        tight_layout = False,
                        plot_pal_events = True, plot_isr_events=True,
                        isr_label_ratio = 1.1,
                        legend_label_ratio = 1,
                        filter_by = None,
                        caption_col  = "Caption",
                        plot_isr_label_up = False
                        ):

    v_label_font = plot_fonts
    legend_font = plot_fonts
    axis_tick_font = plot_fonts
    axis_label_font = plot_fonts
    
        
    # [2.1] Import Critical Events
    
    # -  read the excel containing the events data
    
    df_events = pd.read_excel(path_critical_events, sheet_name = "Final_List")
    
    # -  convert dates from str to datetime & extract dates only
    df_events['Date'] = pd.to_datetime(df_events['Date'], format = "%Y-%m-%d").copy()
    
    df_events['Date'] = df_events['Date'].dt.date
    
    
    # -  convert dates from str to datetime & extract dates only
    df_events['Label_Date'] = pd.to_datetime(df_events['Label_Date'], format = "%Y-%m-%d").copy()
    
    df_events['Label_Date'] = df_events['Label_Date'].dt.date
    
    # -  remove any white spaces before or after the caption labels of v lines
    df_events['Caption'] = df_events['Caption'].str.strip()


    # -  filter events by source list
    filter_event_src = df_events['Source List']!='Manually Collected'
    
    df_events = df_events[filter_event_src].copy()
    
    df_events = df_events.fillna("").copy()
            

    # [2.2] Plot the critical events as vertical lines
    
    if ax_i == '':
        fig_i, ax_i = plt.subplots(figsize=(fig_x, fig_y), dpi=res_dpi)


    if plot_vline == True:

        # - mark critical events with vertical grey lines
        if "Date" in data.columns:
            vertical_label_max = pal_label_ratio * data.drop(['Date'], axis=1).max().max()
        else:
            vertical_label_max = pal_label_ratio * data.max().max()

        if set_y_lim != False:
            vertical_label_max = v_label_max_manual


        for _, row in df_events.iterrows():

            # plot pal events labels on top
            if (plot_pal_events == True) & (row['Affected']=='Palestine'):
                ax_i.text(x=row['Label_Date']- timedelta(days=3),
                            y=vertical_label_max,
                            s= str(row[caption_col]),
                            va="bottom",
                            ha ='left',
                            rotation = 'vertical',
                            fontsize=v_label_font,
                            color = color_dict[row['Affected']])


            # - plot isr events labels below the plot

            if (plot_isr_events == True) & (row['Affected']=='Israel'):

                if plot_isr_label_up == True:
                    isr_label_y = vertical_label_max
                    isr_va = "bottom"

                else:
                    isr_label_y = -20 * isr_label_ratio
                    isr_va = "top"

                ax_i.text(x=row['Label_Date']- timedelta(days=3),
                            y= isr_label_y,
                            s= str(row[caption_col]),
                            va= isr_va,
                            ha ='left',
                            rotation = 'vertical',
                            fontsize=v_label_font,
                            color = color_dict[row['Affected']])


            # - plot the vertical lines for both
            ax_i.axvline(x=row['Date'],
                         ls="dashed",
                         color=color_dict[row['Affected']],
                         alpha=0.55)


    # [2.3] Plot the weekly counts using a lineplot
    
    import seaborn as sns

    sns.set_style("whitegrid", {'axes.grid' : False})
    sns.set_color_codes("pastel")

    # - reorder data to present news sources alphabetically-ordered in the legend
    col_order = list(src_dict.keys())
    
    data = data[col_order].copy()

    # - plot the data
    sns.lineplot(data=data,
                 palette = color_dict,
                 ax = ax_i,
                 linewidth=8,
                 dashes=False,
                 legend= plot_legend)

    sns.despine()


    # [2.4] Adjust the plot axes ticks, titles and legend
    
    if x_label=='':
        ax_i.set(xlabel=None)
    else:
        ax_i.set_xlabel(x_label, fontweight='bold', fontsize = axis_label_font)

    ax_i.set_ylabel(y_label, fontweight='bold', fontsize = axis_label_font, labelpad=26)
    if set_y_lim != False:
        ax_i.set_ylim(top = set_y_lim)


    if plot_legend == True:

        legend_ax = ax_i.legend(bbox_to_anchor=(0.5, 1.3*legend_label_ratio), loc='center',
                    borderaxespad=0, ncol=4, fontsize=legend_font)

        for line in legend_ax.get_lines():
            line.set_linewidth(10)


    ax_i.tick_params(axis='both', which='both', labelsize=axis_tick_font,
                     direction = 'inout', labelbottom=True, length=10)

    ax_i.xaxis.set_major_locator(mdates.MonthLocator())
    ax_i.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))

    if tight_layout == True:
        plt.tight_layout()

    plt.subplots_adjust(hspace=pad_plot)

    return None




# [3] Function takes in date-indexed data and smooths the lines using 
#     interpolation that is tuned based on the desired resolution (res variable)

def smooth_plot (data, res = 1000):

    smoothed_data = pd.DataFrame({'Date':data.index})

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




# [4] Run the Plotting and Smoothing Functions from [2] and [3] to plot Fig 1B
plot_multiple_lines(
                    data                = smooth_plot(total_art),
                    x_label             = " ",
                    y_label             = "Article Count",
                    title               = 'Fig 1 - Total Counts',
                    fig_x               = figsize_x,
                    fig_y               = 15,
                    ax_i                = ax1[1],
                    plot_fonts          = main_plot_font,
                    pad_plot            = 1.1,
                    pal_label_ratio     = 1.05,
                    isr_label_ratio     = 1.0,
                    plot_legend         = True,
                    )



# [5] Tweak the plot 
ax1[1].legend(bbox_to_anchor=(0.5, 1.5), loc='center', borderaxespad=0, ncol=4, fontsize=36)

plt.tight_layout()

fig1.subplots_adjust(hspace=0.8)



# [6] Export Fig 1 = Fig 1A + Fig 1B

print("\nExporting Fig 1A and 1B as Fig 1")

title_i = 'Fig 1 - Total Number of Relevant Articles per News Source.svg'
plt.savefig(analysis_output+title_i, bbox_inches="tight", pad_inches=0.5)


print("\nDone!")
