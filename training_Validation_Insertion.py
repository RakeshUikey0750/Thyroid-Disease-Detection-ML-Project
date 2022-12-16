from Training_FileToDB.combined_csv import csv_Operations
from Training_Raw_data_validation.rawValidation import Raw_Data_validation
from DataTypeValidation_Insertion_Training.DataTypeValidation import dBOperation
from DataTransform_Training.DataTransformation import dataTransform
from application_logging import logger


class train_validation:
    def __init__(self, path):
        self.raw_data = Raw_Data_validation(path)
        self.csv_Operations = csv_Operations()
        self.dataTransform = dataTransform()
        self.dBOperation = dBOperation()
        self.file_object = open("Training_Logs/Training_Main_Log.txt", 'a+')
        self.log_writer = logger.App_Logger()

    def train_validation(self):
        try:
            self.log_writer.log(self.file_object, 'Start of Validation on files for Training!!')
            # extracting values from prediction schema
            LengthOfDateStampInFile, LengthOfTimeStampInFile, column_names, NoOfColumns = self.raw_data.valuesFromSchema()
            # getting the regex defined to validate filename
            regex = self.raw_data.manualRegexCreation()
            # validating filename of prediction files
            self.raw_data.validationFileNameRaw(regex, LengthOfDateStampInFile, LengthOfTimeStampInFile)
            # validating column length in the file
            self.raw_data.validateColumnLength(NoOfColumns)
            # validating if any column has all values missing
            self.raw_data.validateMissingValuesInWholeColumn()
            self.log_writer.log(self.file_object, "Raw Data Validation Complete!!")

            # Combining all Training Batch files into one for database insertion
            self.log_writer.log(self.file_object, 'Combining all Training Batch files into one for database insertion')
            self.csv_Operations.combine_all_csv()
            self.log_writer.log(self.file_object, 'Combining all Training files into one is successful')

            self.log_writer.log(self.file_object,
                                "Creating Training_Database and tables on the basis of given schema!!!")
            # create database, if present open the connection! Create table with columns given in schema
            self.dBOperation.createTableDb()
            self.log_writer.log(self.file_object, "Table creation Completed!!")
            self.log_writer.log(self.file_object, "Insertion of Data into Table started!!!!")
            # insert csv files in the table
            self.dBOperation.insertIntoTableGoodData()
            self.log_writer.log(self.file_object, "Insertion in Table completed!!!")
            self.log_writer.log(self.file_object, "Deleting Good Data Folder!!!")
            # Delete the good data folder after loading files in table
            self.raw_data.deleteExistingGoodDataTrainingFolder()
            self.log_writer.log(self.file_object, "Good_Data folder deleted!!!")
            self.log_writer.log(self.file_object, "Moving bad files to Archive and deleting Bad_Data folder!!!")
            # Move the bad files to archive folder
            self.raw_data.moveBadFilesToArchiveBad()
            self.log_writer.log(self.file_object, "Bad files moved to archive!! Bad folder Deleted!!")
            self.log_writer.log(self.file_object, "Validation Operation completed!!")
            self.log_writer.log(self.file_object, "Extracting csv file from table")
            # export data in table to csvfile
            self.dBOperation.selectingDatafromtableintocsv()
            self.log_writer.log(self.file_object, "Validation of Training completed successfully!!")
            self.file_object.close()

        except Exception as e:
            self.log_writer.log(self.file_object, "Error occurred while validating training file: %s" + str(e))
            self.file_object.close()
            raise e
