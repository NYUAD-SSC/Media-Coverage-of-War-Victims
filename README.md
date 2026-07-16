# Media-Coverage-of-War-Victims

This is the code related to manuscript "Media Coverage of War Victims: Journalistic Biases in Reporting on Israel and Gaza"

In this study, we imported raw news articles from the LexisNexis (LN) database and the BBC website for use in our academic research, in accordance with the permissions granted by each provider. The dataset used in the analysis, hereafter referred to as the primary dataset, was derived from these raw articles and serves as the starting point for all analyses described below. 

Note: Due to the terms of the agreements between NYU and LexisNexis and between NYU and the BBC, the complete raw dataset cannot be publicly shared. However, anyone affiliated with universities that have a LexisNexis subscription should also be able to retrieve the relevant articles directly through the database. Nevertheless, we have provided a random sample of 100 articles - 25 from each news source — for verification and exploratory purposes. The LLM prompts used in the analysis are included in the main manuscript. 

Reviewers who require access to the full dataset solely for the purpose of evaluating the manuscript for publication may contact us at bedoor@nyu.edu. 

From this point onward, we share all data derived from the primary dataset, which constitutes the cleaned and finalized starting point for all subsequent analyses. The data presented before this section are considered only raw data.

Below, following the order of the manuscript, we describe how the corresponding plots, figures, and tables were generated. Each code file its own set of analytical outputs, including the associated plots, figures, and tables. [note: each Python file contains a sufficient description of file paths].




Code 1: "Primary Data Exploration.py" generates the following list of figures:

   Main Figures

   Fig 1: Total Number of Relevant Articles per News Source.

      It is divided into the following subplots:
           
        Fig 1A: The bar plot shows the overall count of relevant articles per each 
                of the four media sources. 
                
        Fig 1B: the timeline plot below shows the same number of articles but 
                spread out over time along with major war events that affected 
                Palestinian and Israeli sides displayed in green and blue 
                respectively. Both plots cover the first 12 months of the conflict.



Code 2: "Individualized Grouped Analysis.py" generates the following list of figures and tables:

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





Code 3: "CVN Analysis.py" generates the following list of figures and tables:

    Main Figures
    
    Fig 3: Results of Quantifying the Human Cost of War Analysis.
           
           It consists of the main subplots:
               
            - Fig 3A: A comparison of the total number of articles published by 
                      each news outlet compared to the subsets containing at 
                      least one CVN about Palestine and those with at least one 
                      CVN about Israel. 
                      
                      
           - Fig 3B: The weekly proportion of expected mentions allocated to 
                     the Palestinian side (∆Pn) based on the baseline model, 
                     shown for each news outlet.
                       
                     
           - Fig 3C: A bar plot displaying the total number of doubt-casting 
                     phrases per source, alongside additional charts breaking 
                     down the counts by the type of doubt-casting technique used 
                     by each outlet.
        
                                      
    Supplementary Figures
    
            Supp Fig 6: Disparity in casualty reporting across media sources.
                        
                        
            Supp Fig 7: Baseline comparison of the expected versus actual number 
                        of casualtyrelated CVN mentions for each news outlet 
                        over time. 
                        
                        
            Supp Fig 8: Proportion of Articles Reporting Child-Related CVNs by 
                        Side and Media Source. 
                  

            Supp Fig 9: Proportion of Articles Reporting Child-Related CVNs by 
                        Side and Media Source for Casualties-related CVNs only.
                        
            
            Supp Fig 15: Figure shows the weekly share of CVN statements 
                         published in 2023/24 that had Casting Doubt phrases in 
                         terms of Source Doubting and Uncertainty in Numbers.
            
    
    Supplementary Tables
    
            Supp Tab 6: Distribution of Civilian Victim Numbers (CVNs) by Type 
                        for Palestine and Israel across the four Media Outlets. 
                        
                        
            Supp Tab 9: Percentage of CVNs Reported with References Across Media 
                        Sources and Sides
                        

            Supp Tab 10: Final List of Doubt-Casting Phrases and Their Categories. 
                         (not generated by code as it is manually entered but 
                          used by supp tables 11 to 14)                             
                             
            Supp Tab 11-14: Breakdown of Doubt-Casting Phrases in Casualty 
                            Reporting Sentences in {source}.
                             
                            
            Supp Tab 15:  Child-related Mentions in Media Coverage of Palestine 
                          and Israel: Counts and Percentages Across Four Outlets 
                          (with baseline reference)
                         
                         

Code 4: "Past Conflicts Analysis.py" generates the following list of figures:

    Supplementary Figures
    
    Supp Fig 12: Ratio of individualized to grouped mentions per side for each 
                 media source across the four wars.
    
    
    
    Supp Fig 13: Actual casualty counts and individualized casualty-related 
                 story percentages per side for each media source.
    
    
    
    Supp Fig 14: Figure shows the overall share of CVN statements that had 
                 Casting Doubt phrases in terms of Source Doubting and 
                 Uncertainty in Numbers.


Finally, the online survey instrument described in Supplementary Note 2, and the anonymized responses of all survey participants can be found in the ‘online survey’ folder
