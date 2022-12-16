import pandas
from file_operations import file_methods
from data_preprocessing import preprocessing
from data_ingestion import data_loader_prediction
from application_logging import logger
from Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation
import pickle


class prediction:

    def __init__(self, path):
        self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.App_Logger()
        self.pred_data_val = Prediction_Data_validation(path)

    def predictionFromModel(self):

        try:
            self.pred_data_val.deletePredictionFile()  # deletes the existing prediction file from last run!
            self.log_writer.log(self.file_object, 'Start of Prediction')
            data_getter = data_loader_prediction.Data_Getter_Pred(self.file_object, self.log_writer)
            data = data_getter.get_data()

            preprocessor = preprocessing.Preprocessor(self.file_object, self.log_writer)
            data = preprocessor.dropUnnecessaryColumns(data,
                                                       ['serial_no', 'tsh_measured', 't3_measured', 'tt4_measured',
                                                        't4u_measured', 'fti_measured', 'tbg_measured', 'tbg', 'tsh',
                                                        'referral_source'])

            # replacing '?' values with np.nan as discussed in the EDA part

            data = preprocessor.replaceInvalidValuesWithNull(data)

            # get encoded values for categorical data

            data = preprocessor.encodeCategoricalValuesPrediction(data)
            is_null_present = preprocessor.is_null_present(data)
            if is_null_present:
                data = preprocessor.impute_missing_values(data)
            self.log_writer.log(self.file_object, "Imputation of values done successfully")

            # data=data.to_numpy()
            file_loader = file_methods.File_Operation(self.file_object, self.log_writer)
            kmeans = file_loader.load_model('KMeans')
            self.log_writer.log(self.file_object, "Model loading done successfully")

            clusters = kmeans.predict(data)  # drops the first column for cluster prediction
            self.log_writer.log(self.file_object, "Fitting data into clusters done successfully")
            data['clusters'] = clusters
            self.log_writer.log(self.file_object, "cluster column created done successfully")
            clusters = data['clusters'].unique()
            self.log_writer.log(self.file_object, "No. of clusters: ", )
            result = []  # initialize blank list for storing predicitons
            with open('EncoderPickle/enc.pickle',
                      'rb') as file:  # let's load the encoder pickle file to decode the values
                encoder = pickle.load(file)
            self.log_writer.log(self.file_object, "Encoder loaded successfully")

            for i in clusters:
                cluster_data = data[data['clusters'] == i]
                cluster_data = cluster_data.drop(['clusters'], axis=1)
                model_name = file_loader.find_correct_model_file(i)
                model = file_loader.load_model(model_name)
                for val in (encoder.inverse_transform(model.predict(cluster_data))):
                    result.append(val)
            result = pandas.DataFrame(list(zip(result)), columns=['Predictions'])
            self.log_writer.log(self.file_object, "Prediction Result created")
            path = "Prediction_Output_File/Predictions.csv"
            result.to_csv("Prediction_Output_File/Predictions.csv", header=True, index=False,
                          mode="a+")  # appends result to prediction file
            self.log_writer.log(self.file_object, 'End of Prediction')
        except Exception as ex:
            self.log_writer.log(self.file_object, 'Error occurred while running the prediction!! Error:: ' + str(ex))
            raise ex
        return path

