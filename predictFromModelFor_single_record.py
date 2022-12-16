import pandas as pd
import pickle
from application_logging import logger
from file_operations import file_methods


class predicting_single_rec:
    def __init__(self, data):
        self.file_object = open("Prediction_Logs/Prediction_Log_for1.txt", 'a+')
        self.log_writer = logger.App_Logger()
        self.data = data

    def predictionFromModel(self):
        try:
            self.log_writer.log(self.file_object, "Start of Prediction")

            file_loader = file_methods.File_Operation(self.file_object, self.log_writer)
            kmeans = file_loader.load_model('KMeans')

            self.log_writer.log(self.file_object, "Kmeans model loaded")

            with open('EncoderPickle/enc.pickle',
                      'rb') as file:  # let's load the encoder pickle file to decode the values
                encoder = pickle.load(file)

            self.log_writer.log(self.file_object, "Label encoder loaded")

            cluster = kmeans.predict(self.data)
            self.log_writer.log(self.file_object, "Clusters created successfully")

            self.log_writer.log(self.file_object, "Finding best model for clusters")
            model_name = file_loader.find_correct_model_file(cluster[0])

            self.log_writer.log(self.file_object, "Loading model for prediction")
            model = file_loader.load_model(model_name)
            self.log_writer.log(self.file_object, "Loaded model for prediction")
            result = model.predict(self.data)
            self.log_writer.log(self.file_object, "Prediction is Ready")

            # inverse transform
            self.log_writer.log(self.file_object, "Performing inverse transformation for prediction")
            result = encoder.inverse_transform(result)

            self.log_writer.log(self.file_object, "Prediction successfully done!!")

            return result
        except Exception as e:
            self.log_writer.log(self.file_object, 'Error occurred while running the prediction!! Error:: %s' % e)
            raise e

