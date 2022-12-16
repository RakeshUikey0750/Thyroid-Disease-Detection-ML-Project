from os import listdir
import os
import pandas as pd
from application_logging import logger


class csv_Operations:
    """
                  This class shall be used for obtaining single csv file for data insertion into DB.

                  Written By: Rakesh Uikey
                  Version: 1.0
                  Revisions: None
    """

    def __int__(self):
        self.file_object = open("Prediction_Logs/Combine_all_csv.txt", 'a+')
        self.log_writer = logger.App_Logger()

    def combine_all_csv(self):
        """
                       Method Name: combine_all_csv
                       Description: This method combines all the Good data files from the Training Good_Raw folder into
                                     the single csv file
                       Output: None
                       On Failure: Raise Exception

                       Written By: Rakesh Uikey
                       Version: 1.0
                       Revisions: None
        """
        file_object = open("Prediction_Logs/Combine_all_csv.txt", 'a+')
        log_writer = logger.App_Logger()
        log_writer.log(file_object, 'Entered into the combine_all_csv of the csv_operations class')
        try:
            try:
                project_dir = os.getcwd()
                goodFilePath = os.chdir("Prediction_Raw_Files_Validated\\Good_Raw")
                log_writer.log(file_object, 'GoodFile path created successfully')

                # creating the list of all the files present in goodFilePath
                csv_files = [f for f in listdir(goodFilePath)]
                log_writer.log(file_object, 'list of all csv file created successfully')

            except Exception as e:
                log_writer.log(file_object, 'Error occurred in creating list or changing directory: ' + str(e))
                raise e

            # combine all files in the list
            combined_csv = pd.concat([pd.read_csv(f) for f in csv_files])
            log_writer.log(file_object, 'Combining all csv file is  successful')

            # adding extra integer column to solve primary key column issue while inserting data into cassandra DB.
            combined_csv.insert(0, 'serial_no', range(1, len(combined_csv) + 1))
            log_writer.log(file_object, 'Adding serial column at zero\'th  pos. is successful')

            # changing directory to project level to store final csv file at project level
            os.chdir(project_dir)
            log_writer.log(file_object, 'Directory change at project file level is successful')

            # saving final file to csv
            combined_csv.to_csv("Prediction_FileToDB/combined_csv.csv", index=False, encoding='utf-8-sig')
            log_writer.log(file_object, 'Creation of combined_csv.csv file is successful')

            file_object.close()

        except Exception as e:
            log_writer.log(file_object, 'Error occurred while combining_all_csv files: ' + str(e))
            log_writer.log(file_object, 'Unable to load all csv files into one .Exited the combine_all_csv method of '
                                        'csv operations class')
            file_object.close()
            raise e


