import json
from statistics import mode
from app2 import App2
import pyodbc
import pandas as pd
import sqlite3
from datetime import datetime
import json
from types import SimpleNamespace

from model.inputmessagemodel import InputMessageModel

driver_vdi = '{ODBC Driver 17 for SQL Server}'
host_vdi='aftermarket-mhirj.database.windows.net'
database_vdi='MHIRJ_HUMBER'
user_vdi='humber_rw'
password_vdi='nP@yWw@!$4NxWeK6p*ttu3q6'

def connect_database_mdc_message_input(eq_id):
    if eq_id:
        sql = "SELECT * from [dbo].[MDCMessagesInputs] c WHERE c.Equation_ID='" + eq_id + "' "
    else :
        sql = "SELECT * from [dbo].[MDCMessagesInputs]"
    try:
        conn = pyodbc.connect(
            Trusted_Connection='No',
            driver=driver_vdi, host=host_vdi, database=database_vdi,
                              user=user_vdi, password=password_vdi)
                              
        # conn = pyodbc.connect(
        #     Trusted_Connection='No',
        #     driver=App2().db_driver, host=App2().hostname, database=App2().db_name,
        #                       user=App2().db_username, password=App2().db_password)
                              
        print(sql)
        mdcRaw_df = pd.read_sql(sql, conn)
        return mdcRaw_df
    except pyodbc.Error as err:
        print("Couldn't connect to Server")
        print("Error message:- " + str(err))

def db_delete_mdc_messages_input_by_eq_id(eq_id):
    try:
        conn = pyodbc.connect(
            Trusted_Connection='No',
            driver=driver_vdi, host=host_vdi, database=database_vdi,
                              user=user_vdi, password=password_vdi)
                                               
        cursor = conn.cursor()       
        cursor.execute('''
        DELETE from [dbo].[MDCMessagesInputs] WHERE Equation_ID=?
        ''',eq_id)
        conn.commit()
        conn.close()
        return {"message": eq_id+" Successfully Deleted."}
    except Exception as e: 
        print(e)
        return {'message': 'error in '+str(e)}

def db_insert_mdc_messages_input(raw_data):
    print("data : ",raw_data)
    try : 
        model = InputMessageModel(
            raw_data['lru'],
            raw_data['ata'],
            raw_data['message'],
            raw_data['comp_id'],
            raw_data['message1'],
            raw_data['fault_logged'],
            raw_data['status'],
            raw_data['message_type'],
            raw_data['eicas'],
            raw_data['timer'],
            raw_data['logic'],
            raw_data['equation_description'],
            raw_data['equation_id'],
            raw_data['occurance_flag'],
            raw_data['days_count'],
            raw_data['priority'],
            raw_data['recommended_actions'],
            raw_data['additional_comment'],
            raw_data['ise_input'],
            raw_data['ata_main'],
            raw_data['ata_sub'],
        )
        print('raw_data lru ',model.lru)
        conn = pyodbc.connect(
            Trusted_Connection='No',
            driver=driver_vdi, host=host_vdi, database=database_vdi,
                              user=user_vdi, password=password_vdi)
                                               
        cursor = conn.cursor()       
        cursor.execute('''
        INSERT INTO [dbo].[MDCMessagesInputs](
        [LRU],
        [ATA],
        [Message],
        [Comp_ID],
        [Message1],
        [Fault_Logged],
        [Status],
        [Message_Type],
        [EICAS],
        [Timer],
        [Logic],
        [Equation_Description],
        [Equation_ID],
        [Occurance_Flag],
        [Days_Count],
        [Priority],
        [MHIRJ_ISE_reccomended_actions],
        [Additional_comment],
        [MHIRJ_ISE_inputs],
        [ATA_Main],
        [ATA_Sub]
       )
       VALUES
       (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
       ''',
       model.lru,
       model.ata,
       model.message,
       model.comp_id,
       model.message1,
       model.fault_logged,
       model.status,
       model.message_type,
       model.eicas,
       model.timer,
       model.logic,
       model.equation_description,
       model.equation_id,
       model.occurance_flag,
       model.days_count,
       model.priority,
       model.recommended_actions,
       model.additional_comment,
       model.ise_input,
       model.ata_main,
       model.ata_sub
       )
        conn.commit()
        return {"message":"Data Successfully Inserted."}
    except Exception as e: 
        print(e)
        return {'message': 'error in '+str(e)}


def connect_to_fetch_all_ata(from_dt, to_dt):
    all_ata_query = "SELECT DISTINCT SUBSTRING(ATA, 0, CHARINDEX('-', ATA)) AS ATA_Main FROM MDC_MSGS WHERE MSG_Date BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    # all_ata_query = "SELECT DISTINCT ATA_Main from Airline_MDC_Data WHERE DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    try:
        conn = pyodbc.connect(driver=driver_vdi, host='aftermarket-mhirj.database.windows.net', database='MDP-Dev',
                    user='humber_ro', password='Container-Zesty-Wriggly7-Catalog')
        all_ata_df = pd.read_sql(all_ata_query, conn)

        return all_ata_df
    except pyodbc.Error as err:
        print("Couldn't connect to Server")
        print("Error message:- " + str(err))

def connect_to_fetch_all_eqids(from_dt, to_dt):
    all_ata_query = "SELECT DISTINCT MDC_MSGS.EQ_ID FROM MDC_MSGS WHERE MSG_Date BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    # all_ata_query = "SELECT DISTINCT Equation_ID from Airline_MDC_Data WHERE DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    try:
        conn = pyodbc.connect(driver=driver_vdi, host='aftermarket-mhirj.database.windows.net', database='MDP-Dev',
                    user='humber_ro', password='Container-Zesty-Wriggly7-Catalog')
        all_eqid_df = pd.read_sql(all_ata_query, conn)

        return all_eqid_df
    except pyodbc.Error as err:
        print("Couldn't connect to Server")
        print("Error message:- " + str(err))

def connect_database_MDCdata(ata, excl_eqid, include_current_message, from_dt, to_dt):
    global MDCdataDF
    global airline_id
    all_ata_str_list = []
    all_ata_str = ""
    all_eqid_str = ""
    from_dt = from_dt + " 00:00:00"
    to_dt = to_dt + " 23:59:59"
    airline_operator = "SKW"

    if ata == 'ALL':
        all_ata = connect_to_fetch_all_ata(from_dt, to_dt)

        all_ata_str = "("
        all_ata_list = all_ata['ATA_Main'].tolist()
        for each_ata in all_ata_list:
            all_ata_str_list.append(str(each_ata))
            all_ata_str += "'"+str(each_ata)+"'"
            if each_ata != all_ata_list[-1]:
                all_ata_str += ","
            else:
                all_ata_str += ")"
        # print(all_ata_str)
        ata = ""

    if excl_eqid == 'NONE':
        all_eqid = connect_to_fetch_all_eqids(from_dt, to_dt)

        all_eqid_str = "("
        all_eqid_list = all_eqid['EQ_ID'].tolist()
        for each_eqid in all_eqid_list:
            #all_eqid_str_list.append(str(each_eqid))
            all_eqid_str += "'" + str(each_eqid) + "'"
            if each_eqid != all_eqid_list[-1]:
                all_eqid_str += ","
            else:
                all_eqid_str += ")"
        print(all_eqid_str)
    # connecting to the database
    # sql = f'''SELECT * FROM MDC_MSGS WHERE (MSG_Date BETWEEN  {from_dt} AND {to_dt}) AND ({f"SUBSTRING(ATA, 0, CHARINDEX('-', ATA)) IN {str(all_ata_str)} OR " if all_ata_str else f"SUBSTRING(ATA, 0, CHARINDEX('-', ATA)) IN {str(ata)} OR " if ata != 'ALL' else 
    # f"SUBSTRING(ATA, 0, CHARINDEX('-', ATA)) IN {str(ata)} OR " if ata else ''} {f"EQ_ID IN {str(all_eqid_str)} OR " if all_eqid_str else ''} {f"OPERATOR = {str(airline_id)}" if airline_id else ''} AND flight_phase IS NOT NULL AND INTERMITNT IS NOT NULL) '''
    sql = f"SELECT * FROM MDC_MSGS WHERE (MSG_Date BETWEEN '{from_dt}' AND '{to_dt}') AND (OPERATOR = '{airline_operator}')"
    if ata or all_ata_str or all_eqid_str or excl_eqid or include_current_message:
        sql += ' AND'
        if ata != 'ALL' and ata:
            sql += f"(SUBSTRING(ATA, 0, CHARINDEX('-', ATA)) IN {str(ata)}) AND"
        if all_ata_str:
            sql += f"(SUBSTRING(ATA, 0, CHARINDEX('-', ATA)) IN {str(all_ata_str)}) AND"
        if all_eqid_str:
            sql += f"(EQ_ID IN {str(all_eqid_str)}) AND"
        if excl_eqid != 'NONE' and excl_eqid:
            sql += f"(EQ_ID IN {str(excl_eqid)}) AND"
        if include_current_message == 0:
            sql += "(flight_phase IS NOT NULL AND INTERMITNT IS NOT NULL)"
        if sql.split()[-1] == "AND":
            sql = sql[:-4]
    

    # if include_current_message == 0: 
  
    # else :
    #     sql = "SELECT * FROM MDC_MSGS WHERE SUBSTRING(ATA, 0, CHARINDEX('-', ATA)) IN " + str(all_ata_str) + " OR EQ_ID IN " + str(all_eqid_str) + " OR OPERATOR = " + str(airline_id) + " AND MSG_Date BETWEEN " + from_dt + " AND " + to_dt + ""
    # # else:
    # #     sql = "SELECT * FROM MDC_MSGS WHERE MSG_Date BETWEEN '" + from_dt + "' AND '" + to_dt + "'"

    column_names = ["Aircraft", "Tail#", "Flight Leg No",
            "ATA Main", "ATA Sub", "ATA", "ATA Description", "LRU",
            "DateAndTime", "MDC Message", "Status", "Flight Phase", "Type",
            "Intermittent", "Equation ID", "Source", "Diagnostic Data",
            "Data Used to Determine Msg", "ID", "Flight", "airline_id", "aircraftno"]
    
    try:
        conn = pyodbc.connect(driver=driver_vdi, host='aftermarket-mhirj.database.windows.net', database='MDP-Dev',
                        user='humber_ro', password='Container-Zesty-Wriggly7-Catalog')
        MDCdataDF = pd.read_sql(sql, conn)
        # MDCdataDF.columns = column_names
        return MDCdataDF
    except pyodbc.Error as err:
        print("Couldn't connect to Server")
        print("Error message:- " + str(err))

    # # If we do not want to include current message -> exclude null flight phase and null intermittents
    # if include_current_message == 0:    
    #     if ata == 'ALL' and excl_eqid == 'NONE':
    #         sql = "SELECT * FROM Airline_MDC_Data WHERE ATA_Main IN " + str(all_ata_str) + " AND Equation_ID IN " + str(
    #             all_eqid_str) + " AND airline_id = " + str(
    #             airline_id) + " AND flight_phase IS NOT NULL AND Intermittent IS NOT NULL AND DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    #     elif excl_eqid == 'NONE':
    #         sql = "SELECT * FROM Airline_MDC_Data WHERE ATA_Main IN " + str(ata) + " AND Equation_ID IN " + str(
    #             all_eqid_str) + " AND airline_id = " + str(
    #             airline_id) + " AND flight_phase IS NOT NULL AND Intermittent IS NOT NULL AND DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    #     elif ata == 'ALL':
    #         sql = "SELECT * FROM Airline_MDC_Data WHERE ATA_Main IN " + str(all_ata_str) + " AND Equation_ID NOT IN " + str(
    #             excl_eqid) + " AND airline_id = " + str(
    #             airline_id) + " AND flight_phase IS NOT NULL AND Intermittent IS NOT NULL AND DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    #     else:
    #         sql = "SELECT * FROM Airline_MDC_Data WHERE ATA_Main IN " + str(ata) + " AND Equation_ID NOT IN " + str(
    #             excl_eqid) + " AND airline_id = " + str(
    #             airline_id) + " AND flight_phase IS NOT NULL AND Intermittent IS NOT NULL AND DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"

    # elif include_current_message == 1:
    #     if ata == 'ALL' and excl_eqid =='NONE':
    #         sql = "SELECT * FROM Airline_MDC_Data WHERE ATA_Main IN " + str(all_ata_str) + " AND Equation_ID IN " + str(
    #             all_eqid_str) + " AND airline_id = " + str(
    #             airline_id) + " AND DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    #     elif ata == 'ALL':
    #         sql = "SELECT * FROM Airline_MDC_Data WHERE ATA_Main IN " + str(all_ata_str) + " AND Equation_ID NOT IN " + str(
    #             excl_eqid) + " AND airline_id = " + str(
    #             airline_id) + " AND DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    #     elif excl_eqid == 'NONE':
    #         sql = "SELECT * FROM Airline_MDC_Data WHERE ATA_Main IN " + str(ata) + " AND Equation_ID IN " + str(
    #             all_eqid_str) + " AND airline_id = " + str(
    #             airline_id) + " AND DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"
    #     else:
    #         sql = "SELECT * FROM Airline_MDC_Data WHERE ATA_Main IN " + str(ata) + " AND Equation_ID NOT IN " + str(
    #             excl_eqid) + " AND airline_id = " + str(
    #             airline_id) + " AND DateAndTime BETWEEN '" + from_dt + "' AND '" + to_dt + "'"

  
    # try:
    #     conn = pyodbc.connect(driver=db_driver, host=hostname, database=db_name,
    #                           user=db_username, password=db_password)
    #     MDCdataDF = pd.read_sql(sql, conn)
    #     MDCdataDF.columns = column_names
    #     return MDCdataDF
    # except pyodbc.Error as err:
    #     print("Couldn't connect to Server")
    #     print("Error message:- " + str(err))
        
#corelation connect database 
def connect_database_for_corelation(from_dt, to_dt, equation_id, tail_no):
    sql =""

    sql += "SELECT DISTINCT [ATA_Main],[ATA_Sub],[MaintTransID],[DateAndTime],[Failure_Flag],[MRB],[SquawkSource],[Discrepancy],[CorrectiveAction] FROM [dbo].[MDC_PM_Correlated_Test] WHERE CONVERT(date,DateAndTime) BETWEEN '" + from_dt + "'  AND '" + to_dt + "'"
    
    if equation_id : 
        sql+= " AND EQ_ID = '"+equation_id+"'"
    if tail_no : 
        sql += " AND Aircraft_tail_No ='"+tail_no+"'"
    print(sql)
    try:
        conn = pyodbc.connect(driver=driver_vdi, host=host_vdi,
                              database=database_vdi,
                              user=user_vdi, password=password_vdi)
        report_eqId_sql_df = pd.read_sql(sql, conn)
        conn.close()
        return report_eqId_sql_df
    except pyodbc.Error as err:
        print("Couldn't connect to Server")
        print("Error message:- " + str(err))
        return {"message":str(err)}

def connect_database_for_corelation_pid(p_id):
    
    sql = """SELECT 
	[Aircraft_tail_No],
	[EQ_ID],
	[aircraftno],
	[ATA_Description],
	[LRU],
	[CAS],
	[MDC_MESSAGE],
	[EQ_DESCRIPTION],
	[ATA_Main],
	[ATA_Sub]
    FROM [dbo].[MDC_PM_Correlated_Test] 
    WHERE [MaintTransID] = %s
    """ %(p_id)

    print(sql)

    try:
        conn = pyodbc.connect(driver=driver_vdi, host=host_vdi,
                              database=database_vdi,
                              user=user_vdi, password=password_vdi)
        corelation_df = pd.read_sql(sql, conn)
        conn.close()
        return corelation_df
    except pyodbc.Error as err:
        print("Couldn't connect to Server")
        print("Error message:- " + str(err))
        return {"message":str(err)}

def connect_database_for_corelation_ata(from_dt, to_dt, equation_id, ata):
    sql =""

    sql += "SELECT DISTINCT [ATA_Main],[ATA_Sub],[MaintTransID],[DateAndTime],[Failure_Flag],[MRB],[SquawkSource],[Discrepancy],[CorrectiveAction] FROM [dbo].[MDC_PM_Correlated_Test] WHERE CONVERT(date,DateAndTime) BETWEEN '" + from_dt + "'  AND '" + to_dt + "'"
    #if "ALL" not in ata:
#     #    ata = str(tuple(ata.replace(")", "").replace("(", "").replace("'", "").split(",")))


    print("len of eq_id",equation_id)
    if equation_id!="":
        equation_id = str(tuple(equation_id.replace(")","").replace("(","").replace("'","").split(",")))
        if len(equation_id) <= 14:
            equation_id = equation_id.replace(equation_id[len(equation_id)-2], '')
        sql += "  AND EQ_ID IN " + equation_id
    if "ALL" not in ata :
        if ata!="":
            sql += "  AND ATA_Main IN " + ata
    if ata:
        ata = str(tuple(ata.replace(")","").replace("(","").replace("'","").split(",")))
    print(sql)
    try:
        conn = pyodbc.connect(driver=driver_vdi, host=host_vdi,
                              database=database_vdi,
                              user=user_vdi, password=password_vdi)
        sql_df = pd.read_sql(sql, conn)
        conn.close()
        return sql_df
    except pyodbc.Error as err:
        print("Couldn't connect to Server")
        print("Error message:- " + str(err))
        return {"message":str(err)}