import csv
import os
import pandas as pd
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from application_logging.logger import App_Logger


class dBOperation:
    """
         This class shall be used for handling all the Cassandra Database operations.

         Written By: Rakesh Uikey
         Version: 1.0
         Revisions: None
      """

    def __init__(self):
        self.logger = App_Logger()
        self.secure_connect_bundle = 'secure-connect-prediction.zip'
        self.client_id = 'gCPCZSwtUOgJAKwgQRjTaOzc'
        self.client_secret = 'qA_viKt8U7GGZa7e0lzG1x9X2w+j_l9563CmKbTqx27k9e2N_e5l_QEshCJFxS6s-92HxBSXR-+809olm+FvLMsTr9.-b,2wuRaNDu5rHhM5NK92woCndUWuYivFXFsW'

    def dataBaseConnection(self):
        """
                Method Name: dataBaseConnection
                Description: This method creates the database and if Database already exists then opens the connection
                to the DB.
                Output: Connection to the DB
                On Failure: Raise Connection Error

                Written By: Rakesh Uikey
                Version: 1.0
                Revisions: None

        """
        try:
            cloud_config = {
                'secure_connect_bundle': self.secure_connect_bundle
            }
            auth_provider = PlainTextAuthProvider(self.client_id, self.client_secret)
            cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            session = cluster.connect()
            session.execute("select release_version from system.local").one()

            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, " Cassandra database connected successfully")
            file.close()
        except ConnectionError:
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, "Error while connecting to database: %s" % ConnectionError)
            file.close()
            raise ConnectionError
        return session

    def createTableDb(self):
        """
                        Method Name: createTableDb
                        Description: This method creates a table in the given database which will be used to insert
                                     the Good data after raw data validation.
                        Output: None
                        On Failure: Raise Exception

                        Written By: Rakesh Uikey
                        Version: 1.0
                        Revisions: None

                        """
        session = self.dataBaseConnection()
        try:
            session.execute('use training;')
            session.execute('DROP TABLE IF EXISTS Good_Raw_Data;')
            session.execute("CREATE TABLE Good_Raw_Data (serial_no int PRIMARY KEY, age int, sex varchar, "
                            "on_thyroxine varchar,query_on_thyroxine varchar,on_antithyroid_medication varchar,"
                            "sick varchar,pregnant varchar,thyroid_surgery varchar, I131_treatment varchar, "
                            "query_hypothyroid varchar, query_hyperthyroid varchar, lithium varchar, "
                            "goitre varchar, tumor varchar, hypopituitary varchar, psych varchar, TSH_measured "
                            "varchar, TSH varchar, T3_measured varchar, T3 varchar, TT4_measured varchar, "
                            "TT4 varchar, T4U_measured varchar, T4U varchar, FTI_measured varchar, FTI varchar, "
                            "TBG_measured varchar, TBG varchar, referral_source varchar, Class varchar);")
            file = open("Training_Logs/DbTableLog.txt", 'a+')
            self.logger.log(file, "Tables created successfully!!")
            session.shutdown()
            self.logger.log(file, "Database closed successfully!!")
            file.close()

        except Exception as e:
            file = open("Training_Logs/DbTableLog.txt", 'a+')
            self.logger.log(file, "Error while creating table: %s " % e)
            session.shutdown()
            self.logger.log(file, "Database closed successfully")
            file.close()
            raise e

    def insertIntoTableGoodData(self):
        """
                               Method Name: insertIntoTableGoodData
                               Description: This method inserts the Good data files from the Good_Raw folder into the
                                            above created table.
                               Output: None
                               On Failure: Raise Exception

                               Written By: Rakesh Uikey
                               Version: 1.0
                               Revisions: None

        """
        session = self.dataBaseConnection()
        session.execute('USE training;')

        log_file = open("Training_Logs/DbInsertLog.txt", 'a+')
        self.logger.log(log_file, 'Data insertion started')
        try:
            # Opening csv file for data insertion into DB
            with open("Training_FileToDB/combined_csv.csv", "r") as f:
                next(f)
                reader = csv.reader(f, delimiter=",")
                for i in reader:
                    session.execute(
                        'insert into Good_Raw_Data (serial_no, age, sex, on_thyroxine, query_on_thyroxine, '
                        'on_antithyroid_medication, sick, pregnant, thyroid_surgery, I131_treatment, '
                        'query_hypothyroid,query_hyperthyroid, lithium, goitre, tumor, hypopituitary,psych, '
                        'TSH_measured, TSH, T3_measured, T3, TT4_measured, TT4, T4U_measured, T4U,FTI_measured, FTI, '
                        'TBG_measured, TBG,referral_source, Class) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'
                        '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        [int(i[0]), int(i[1]), i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], i[12],
                         i[13], i[14], i[15], i[16], i[17], i[18], i[19], i[20], i[21], i[22], i[23], i[24], i[25],
                         i[26], i[27], i[28], i[29], i[30]])
            self.logger.log(log_file, 'Data inserted into cassandra DB successfully')
            session.shutdown()

        except Exception as e:
            self.logger.log(log_file, 'Error occurred while Data inserting into cassandra DB: ' + str(e))
            log_file.close()
            session.shutdown()
            raise e

    def selectingDatafromtableintocsv(self):
        """
                               Method Name: selectingDatafromtableintocsv
                               Description: This method exports the data in GoodData table as a CSV file at given
                                            specific location.
                               Output: None
                               On Failure: Raise Exception

                               Written By: Rakesh Uikey
                               Version: 1.0
                               Revisions: None

        """

        fileFromDb = 'Training_FileFromDB/'
        fileName = 'InputFile.csv'
        log_file = open("Training_Logs/ExportToCsv.txt", 'a+')
        self.logger.log(log_file, 'Entered into select data from database method')
        session = self.dataBaseConnection()
        session.execute('USE training')
        try:
            # Opening empty list for storing selected data from DB
            db_data_list = []
            query = ("SELECT serial_no,age,sex,on_thyroxine,query_on_thyroxine,on_antithyroid_medication,sick,pregnant,"
                     "thyroid_surgery,I131_treatment,query_hypothyroid,query_hyperthyroid,lithium,goitre,tumor,"
                     "hypopituitary,psych,TSH_measured,TSH,T3_measured,T3,TT4_measured,TT4,T4U_measured,T4U,"
                     "FTI_measured,FTI,TBG_measured,TBG,referral_source,Class "
                     "FROM training.Good_Raw_Data;")

            for i in session.execute(query):
                db_data_list.append(i)

            # converting main_list to data frame
            df = pd.DataFrame(db_data_list)

            # Make the CSV output directory
            if not os.path.isdir(fileFromDb):
                os.makedirs(fileFromDb)

            # saving the data frame df to output directory
            df.to_csv(f"{fileFromDb}" + '//' + f"{fileName}", index=False, encoding='utf-8-sig')

            self.logger.log(log_file, "File exported successfully!!!")
            log_file.close()
            session.shutdown()

        except Exception as e:
            self.logger.log(log_file, "File exporting failed. Error : %s" + str(e))
            log_file.close()
            session.shutdown()
            raise e
