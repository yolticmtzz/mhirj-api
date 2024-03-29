from GenerateReport.helper import LongestConseq, check_2in5, connect_database_MDCdata, connect_database_MDCmessagesInputs, connect_database_TopMessagesSheet, connect_to_fetch_all_jam_messages, highlightJams, isValidParams
import numpy as np
import pandas as pd


def historyReport(MaxAllowedOccurrences: int, MaxAllowedConsecLegs: int, MaxAllowedIntermittent: int, MaxAllowedConsecDays: int, ata: str, exclude_EqID:str, airline_operator: str, include_current_message: int, fromDate: str , toDate: str):
    if isValidParams(MaxAllowedOccurrences, MaxAllowedConsecLegs, MaxAllowedIntermittent, MaxAllowedConsecDays, ata, exclude_EqID, airline_operator, include_current_message, fromDate, toDate):
        MDCdataDF = connect_database_MDCdata(ata, exclude_EqID, airline_operator, include_current_message, fromDate, toDate)
        MDCdataDF["MSG_Date"] = pd.to_datetime(MDCdataDF["MSG_Date"]) # formatting for date
        MDCdataDF["FLIGHT_LEG"].fillna(value= 0.0, inplace= True) # Null values preprocessing - if 0 = Currentflightphase
        MDCdataDF["FLIGHT_PHASE"].fillna(False, inplace= True) # NuCell values preprocessing for currentflightphase
        MDCdataDF["INTERMITNT"].fillna(value= 0.0, inplace= True) # Null values preprocessing for currentflightphase
        MDCdataDF["INTERMITNT"].replace(to_replace= ">", value= "9", inplace=True) # > represents greater than 8 INTERMITNT values
        MDCdataDF["INTERMITNT"].replace(to_replace= ">9", value= "9", inplace=True)
        # try:                      
        #     print("data in intermittent ",MDCdataDF["INTERMITNT"])            
        #     MDCdataDF["INTERMITNT"] = int(MDCdataDF["INTERMITNT"]) # cast type to int
        # except:
        #     #print("data in intermittent exec",MDCdataDF["INTERMITNT"])            
        #     MDCdataDF["INTERMITNT"] = 9

        MDCdataDF["AC_SN"] = MDCdataDF["AC_SN"].str.replace('AC', '')
        MDCdataDF.fillna(value= " ", inplace= True) # replacing all REMAINING null values to a blank string
        MDCdataDF.sort_values(by= "MSG_Date", ascending= False, inplace= True, ignore_index= True)

        AircraftTailPairDF = MDCdataDF[["AC_SN", "AC_TN"]].drop_duplicates(ignore_index= True) # unique pairs of AC SN and AC_TN for use in analysis
        AircraftTailPairDF.columns = ["AC SN","AC_TN"] # re naming the columns to match History/Daily analysis output

        # DatesinData = MDCdataDF["MSG_Date"].dt.date.unique() # these are the dates in the data in Datetime format. 
        # NumberofDays = len(MDCdataDF["MSG_Date"].dt.date.unique()) # to pass into Daily analysis number of days in data
        # latestDay = str(MDCdataDF.loc[0, "MSG_Date"].date()) # to pass into history analysis MDCdataDF["MSG_Date"].sort_values().iloc[-1]

        MDCMessagesDF = connect_database_MDCmessagesInputs() # bring messages and inputs into a Dataframe
        TopMessagesDF = connect_database_TopMessagesSheet() # bring messages and inputs into a Dataframe
        TopMessagesArray = TopMessagesDF.to_numpy() # converting to numpy to work with arrays

        if include_current_message == 1:
            # include the current flight legs
            selection = MDCdataDF[["EQ_ID", "AC_SN"]]
            total_occ_DF = selection.value_counts().unstack()
            
            # selecting only the necessary data for - consecutive days
            dates_selection = MDCdataDF[["AC_SN", "EQ_ID", "MSG_Date"]].copy()
            dates_selection.set_index(["AC_SN", "EQ_ID"], inplace= True)
            dates_selection.sort_index(inplace= True)
            
            # selecting only the necessary data for - consecutive legs
            MDCdataDF['FLIGHT_LEG'] = MDCdataDF['FLIGHT_LEG'].astype(int)
            legs_selection = MDCdataDF[["AC_SN", "EQ_ID", "FLIGHT_LEG"]].sort_values(by= ["FLIGHT_LEG"], ascending= False).copy()
            legs_selection.set_index(["AC_SN", "EQ_ID"], inplace= True)
            legs_selection.sort_index(inplace= True)
            
            # selecting only the necessary data for - intermittent
            MDCdataDF['INTERMITNT'] = MDCdataDF['INTERMITNT'].astype(int)
            Intermittent_selection = MDCdataDF[["AC_SN", "EQ_ID", "INTERMITNT"]].copy()
            Intermittent_selection.set_index(["AC_SN", "EQ_ID"], inplace= True)
            Intermittent_selection.sort_index(inplace= True)

        elif include_current_message == 0:
            # exclude the current flight legs
            selection = MDCdataDF[["EQ_ID", "AC_SN", "FLIGHT_LEG"]][MDCdataDF["FLIGHT_LEG"] != 0].copy()
            selection.drop(["FLIGHT_LEG"], inplace= True, axis= 1)
            total_occ_DF = selection.value_counts().unstack()
            
            # selecting only the necessary data for - consecutive days
            dates_selection = MDCdataDF[["AC_SN", "EQ_ID", "MSG_Date", "FLIGHT_LEG"]][MDCdataDF["FLIGHT_LEG"] != 0].copy()
            dates_selection.drop(["FLIGHT_LEG"], inplace= True, axis= 1)
            dates_selection.set_index(["AC_SN", "EQ_ID"], inplace= True)
            dates_selection.sort_index(inplace= True)
            
            # selecting only the necessary data for - consecutive legs
            legs_selection = MDCdataDF[["AC_SN", "EQ_ID", "FLIGHT_LEG"]][MDCdataDF["FLIGHT_LEG"] != 0].sort_values(by= ["FLIGHT_LEG"], ascending= False).copy()
            legs_selection.set_index(["AC_SN", "EQ_ID"], inplace= True)
            legs_selection.sort_index(inplace= True)
            
            # selecting only the necessary data for - intermittent
            Intermittent_selection = MDCdataDF[["AC_SN", "EQ_ID", "INTERMITNT", "FLIGHT_LEG"]][MDCdataDF["FLIGHT_LEG"] != 0].copy()
            Intermittent_selection.drop(["FLIGHT_LEG"], inplace= True, axis= 1)
            Intermittent_selection.set_index(["AC_SN", "EQ_ID"], inplace= True)
            Intermittent_selection.sort_index(inplace= True)

        # obtain location of nonempty values
        b1message, aircraft = np.where(pd.notnull(total_occ_DF))
        # obtains the address to the values to be referenced later
        notEmptyLabelPairs = np.column_stack([total_occ_DF.columns[aircraft],total_occ_DF.index[b1message]])
        # creating a dataframe with a similar size to total occurrences df
        consec_days = pd.DataFrame().reindex_like(total_occ_DF)

        # creating a dataframe with a similar size to total occurrences df
        consec_legs = pd.DataFrame().reindex_like(total_occ_DF)

        # creating a dataframe with a similar size to total occurrences df
        max_intermittent = pd.DataFrame().reindex_like(total_occ_DF)

        # creating a dataframe with a similar size to total occurrences df
        flags_array = pd.DataFrame().reindex_like(total_occ_DF)

        # fill null values with 0
        consec_legs.fillna(value= 0.0, inplace = True)
        consec_days.fillna(value= 0.0, inplace= True)
        max_intermittent.fillna(value= 0.0, inplace= True)
        total_occ_DF.fillna(value= 0.0, inplace= True)
        flags_array.fillna(value= "", inplace= True)

        # Creating flags lists
        flags_jams = MDCMessagesDF.loc[(MDCMessagesDF["Occurrence_Flag"] == 1) & (MDCMessagesDF["Days_Count"] == 0)]["Equation_ID"]
        flags_2in5 = MDCMessagesDF.loc[(MDCMessagesDF["Occurrence_Flag"] == 2) & (MDCMessagesDF["Days_Count"] == 5)]["Equation_ID"]

        # create main table array
        MAINtable_array_temp = np.empty((1,21),object) # 21 = # of columns
        currentRow = 0
        MAINtable_array = []
        count = 0
        # go through AC/eqnID combinations for analysis
        for i in range(len(notEmptyLabelPairs)):
            # pick AC and eqn ID combo
            aircraft = notEmptyLabelPairs[i, 0]
            equation = notEmptyLabelPairs[i, 1]
            
            # set up legs selection for analysis
            legs = legs_selection.loc[aircraft, equation]
            legs = legs["FLIGHT_LEG"].unique()
            
            # set up dates selection for analysis
            dates = dates_selection.loc[aircraft, equation]
            dates = dates["MSG_Date"].dt.date.unique()
            
            # set up intermitt selection for analysis
            intermitt = Intermittent_selection.loc[aircraft, equation].INTERMITNT
            # run 
            consec_days.at[equation, aircraft] = LongestConseq(unique_arr= dates, days_legs= "days")
            consec_legs.at[equation, aircraft] = LongestConseq(unique_arr= legs, days_legs= "legs")
            print("err ", aircraft, type(aircraft))
            max_intermittent.at[equation, float(aircraft)] = max(intermitt)
            
            def f(x):
                return np.int(x)

            f2 = np.vectorize(f)
            
            if total_occ_DF.at[equation, aircraft] >= MaxAllowedOccurrences \
            or consec_days.at[equation, aircraft] >= MaxAllowedConsecDays \
            or consec_legs.at[equation, aircraft] >= MaxAllowedConsecLegs \
            or max_intermittent.at[equation, aircraft] >= MaxAllowedIntermittent \
            or (len(legs) and all(v for v in legs) and f2(legs).any() > 32600) \
            or (flags_jams == equation).any() \
            or ((flags_2in5 == equation).any() and check_2in5(dates)):
                count = count + 1
                if total_occ_DF.at[equation, aircraft] >= MaxAllowedOccurrences:
                    flags_array.at[equation, aircraft] = flags_array.at[equation, aircraft] + "Total occurrences exceeded " + str(MaxAllowedOccurrences) + " occurrences. "
                
                if consec_days.at[equation, aircraft] >= MaxAllowedConsecDays:
                    flags_array.at[equation, aircraft] = flags_array.at[equation, aircraft] + "Maximum consecutive days exceeded " + str(MaxAllowedConsecDays) + " days. "
                    
                if consec_legs.at[equation, aircraft] >= MaxAllowedConsecLegs:
                    flags_array.at[equation, aircraft] = flags_array.at[equation, aircraft] + "Maximum consecutive flight legs exceeded " + str(MaxAllowedConsecLegs) + " flight legs. "
                    
                if max_intermittent.at[equation, aircraft] >= MaxAllowedIntermittent:
                    flags_array.at[equation, aircraft] = flags_array.at[equation, aircraft] + "Maximum intermittent occurrences for one flight leg exceeded " + str(MaxAllowedIntermittent) + " occurrences. "

                if (any(legs) >32600):
                    flags_array.at[equation, aircraft] = flags_array.at[equation, aircraft] + "Flight legs above 32600. "

                if (flags_jams == equation).any():
                    flags_array.at[equation, aircraft] = flags_array.at[equation, aircraft] + str(equation) + " occurred at least once. "

                if ((flags_2in5 == equation).any() and check_2in5(dates)): 
                    flags_array.at[equation, aircraft] = flags_array.at[equation, aircraft] + str(equation) + " occurred at least twice in 5 days. "
               
                #populating the final array (Table)
                MAINtable_array_temp[0,0] = aircraft # SN
                try:
                    MAINtable_array_temp[0,1] = MDCMessagesDF["EICAS"][MDCMessagesDF["Equation_ID"] == equation].item() #EICAS
                except:
                    MAINtable_array_temp[0,1] = "No Data"

                try:
                    MAINtable_array_temp[0,2] = MDCMessagesDF["Message"][MDCMessagesDF["Equation_ID"] == equation].item() #Message
                except:
                    MAINtable_array_temp[0,2] = "No Data" #Message
                
                try:
                    MAINtable_array_temp[0,3] = MDCMessagesDF["LRU"][MDCMessagesDF["Equation_ID"] == equation].item() #LRU
                except:
                    MAINtable_array_temp[0,3] = "No Data"

                try:
                    MAINtable_array_temp[0,4] = MDCMessagesDF["ATA"][MDCMessagesDF["Equation_ID"] == equation].item() #ATA
                except:
                    MAINtable_array_temp[0,4] = "No Data"
                MAINtable_array_temp[0,5] = equation #Eqn ID

                try:
                    MAINtable_array_temp[0,6] = MDCMessagesDF["Message_Type"][MDCMessagesDF["Equation_ID"] == equation].item()
                except:
                    MAINtable_array_temp[0,6] = "No Data"

                try:
                    MAINtable_array_temp[0,7] = MDCMessagesDF["Equation_Description"][MDCMessagesDF["Equation_ID"] == equation].item()
                except:
                    MAINtable_array_temp[0,7] = "No Data"

                MAINtable_array_temp[0,8] = total_occ_DF.at[equation, aircraft]
                MAINtable_array_temp[0,9] = consec_days.at[equation, aircraft]
                MAINtable_array_temp[0,10] = consec_legs.at[equation, aircraft]
                MAINtable_array_temp[0,11] = max_intermittent.at[equation, aircraft]
                MAINtable_array_temp[0,12] = dates.min()
                MAINtable_array_temp[0,13] = dates.max()
                MAINtable_array_temp[0,14] = str(flags_array.at[equation, aircraft])
                #if the input is empty set the priority to 4
                try:
                    if MDCMessagesDF["Priority"][MDCMessagesDF["Equation_ID"] == equation].item() == 0:
                        MAINtable_array_temp[0,15] = 4
                    else:
                        MAINtable_array_temp[0,15] = MDCMessagesDF["Priority"][MDCMessagesDF["Equation_ID"] == equation].item()
                except:
                    MAINtable_array_temp[0,15] = 4

                #For B1-006424 & B1-006430 Could MDC Trend tool assign Priority 3 if logged on A/C below 10340, 15317. Priority 1 if logged on 10340, 15317, 19001 and up
                if equation == "B1-006424" or equation == "B1-006430":
                    if int(aircraft) <= 10340 and int(aircraft) > 10000:
                        MAINtable_array_temp[0,15] = 3
                    elif int(aircraft) > 10340 and int(aircraft) < 11000:
                        MAINtable_array_temp[0,15] = 1
                    elif int(aircraft) <= 15317 and int(aircraft) > 15000:
                        MAINtable_array_temp[0,15] = 3
                    elif int(aircraft) > 15317 and int(aircraft) < 16000:
                        MAINtable_array_temp[0,15] = 1
                    elif int(aircraft) >= 19001 and int(aircraft) < 20000:
                        MAINtable_array_temp[0,15] = 1

                #check content of "MEL or No-Dispatch"
                try:
                    if MDCMessagesDF["MEL_or_No_Dispatch"][MDCMessagesDF["Equation_ID"] == equation].item() == "0":
                        MAINtable_array_temp[0,17] = ""
                    else:
                        MAINtable_array_temp[0,17] = MDCMessagesDF["MEL_or_No_Dispatch"][MDCMessagesDF["Equation_ID"] == equation].item()
                except:
                    MAINtable_array_temp[0,17] = ""
                #check content of "MHIRJ Input"
                try:
                    if MDCMessagesDF["MHIRJ_ISE_inputs"][MDCMessagesDF["Equation_ID"] == equation].item() == "0":
                        MAINtable_array_temp[0,18] = ""
                    else:
                        MAINtable_array_temp[0,18] = MDCMessagesDF["MHIRJ_ISE_inputs"][MDCMessagesDF["Equation_ID"] == equation].item()

                except:
                    MAINtable_array_temp[0,18] = ""
                
                #check the content of MHIRJ ISE recommendation and add to array    
                try:
                    if MDCMessagesDF["MHIRJ_ISE_Recommended_Action"][MDCMessagesDF["Equation_ID"] == equation].item() == "0":
                        MAINtable_array_temp[0,19] = ""
                    else:
                        MAINtable_array_temp[0,19] = MDCMessagesDF["MHIRJ_ISE_Recommended_Action"][MDCMessagesDF["Equation_ID"] == equation].item()
                except:
                    MAINtable_array_temp[0,19] = ""
                #check content of "additional"
                try:
                    if MDCMessagesDF["Additional_Comments"][MDCMessagesDF["Equation_ID"] == equation].item() == "0":
                        MAINtable_array_temp[0,20] = ""
                    else:
                        MAINtable_array_temp[0,20] = MDCMessagesDF["Additional_Comments"][MDCMessagesDF["Equation_ID"] == equation].item()
                except:
                    MAINtable_array_temp[0,20] = ""
                #Check for the equation in the Top Messages sheet
                TopCounter = 0
                Top_LastRow = TopMessagesArray.shape[0]
                while TopCounter < Top_LastRow:

                    #Look for the flagged equation in the Top Messages Sheet
                    if equation == TopMessagesArray[TopCounter,4]:

                        #Found the equation in the Top Messages Sheet. Put the information in the report
                        MAINtable_array_temp[0,15] = "Known Nuissance: " + str(TopMessagesArray[TopCounter, 13]) \
                        + " / In-Service Document: " + str(TopMessagesArray[TopCounter,11]) \
                        + " / FIM Task: " + str(TopMessagesArray[TopCounter,10]) \
                        + " / Remarks: " + str(TopMessagesArray[TopCounter,14])

                        #Not need to keep looking
                        TopCounter = TopMessagesArray.shape[0]

                    else:
                        #Not equal, go to next equation
                        MAINtable_array_temp[0,16] = ""
                        TopCounter += 1
                # End while
                if currentRow == 0:
                    MAINtable_array = np.array(MAINtable_array_temp)      
                else:
                    MAINtable_array = np.append(MAINtable_array,MAINtable_array_temp,axis=0)
                #End if Build MAINtable_array
                
                #Move to next Row on Main page for next flag
                currentRow = currentRow + 1
                    
        TitlesArrayHistory = ["AC SN", "EICAS Message", "MDC Message", "LRU", "ATA", "B1-Equation", "Type",
                    "Equation Description", "Total Occurrences", "Consecutive Days", "Consecutive FL",
                    "INTERMITNT", "Date from", "Date to", "Reason(s) for flag", "Priority", "Known Top Message - Recommended Documents", "MEL or No-Dispatch", 
                    "MHIRJ Input", "MHIRJ Recommendation", "Additional Comments"]

        # Converts the Numpy Array to Dataframe to manipulate
        #pd.set_option('display.max_rows', None)
        # Main table
        OutputTableHistory = pd.DataFrame(data= MAINtable_array, columns= TitlesArrayHistory).fillna(" ")
        OutputTableHistory = OutputTableHistory.merge(AircraftTailPairDF, on= "AC SN") # AC_TN added to the end (last column)
        OutputTableHistory = OutputTableHistory[["AC_TN", "AC SN", "EICAS Message", "MDC Message", "LRU", "ATA", "B1-Equation", "Type",
                    "Equation Description", "Total Occurrences", "Consecutive Days", "Consecutive FL",
                    "INTERMITNT", "Date from", "Date to", "Reason(s) for flag", "Priority", "Known Top Message - Recommended Documents", "MEL or No-Dispatch",
                    "MHIRJ Input", "MHIRJ Recommendation", "Additional Comments"]].sort_values(by= ["Type", "Priority"]) # AC_TN added to output table which means that column order has to be re orderedb8632868 2076
        
        listofJamMessages = ["B1-309178","B1-309179","B1-309180","B1-060044","B1-060045","B1-007973",
                     "B1-060017","B1-006551","B1-240885","B1-006552","B1-006553","B1-006554",
                     "B1-006555","B1-007798","B1-007772","B1-240938","B1-007925","B1-007905",
                     "B1-007927","B1-007915","B1-007926","B1-007910","B1-007928","B1-007920"]
        # all_jam_messages = connect_to_fetch_all_jam_messages()
        # for each_jam_message in all_jam_messages['Jam_Message']:
        #     listofJamMessages.append(each_jam_message)
        # print(listofJamMessages)

        OutputTableHistory = highlightJams(OutputTableHistory, listofJamMessages)
        OutputTableHistory_json = OutputTableHistory.to_json(orient='records')
        return OutputTableHistory
    # else:
        # throw error response
