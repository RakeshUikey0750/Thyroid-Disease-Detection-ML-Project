import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.preprocessing import LabelEncoder
import pickle
from imblearn.over_sampling import RandomOverSampler


class Preprocessor:
    """
             This class shall  be used to clean and transform the data before training.

             Written By: Rakesh Uikey
             Version: 1.0
             Revisions: None

    """

    def __init__(self, file_object, logger_object):
        self.file_object = file_object
        self.logger_object = logger_object

    def separate_label_feature(self, data, label_column_name):
        """
                        Method Name: separate_label_feature
                        Description: This method separates the features and a Label Columns.
                        Output: Returns two separate Dataframes, one containing features and the other containing Labels .
                        On Failure: Raise Exception

                        Written By: Rakesh Uikey
                        Version: 1.0
                        Revisions: None

        """

        self.logger_object.log(self.file_object, 'Entered the separate_label_feature method of the Preprocessor class')
        try:
            # drop the columns specified and separate the feature columns
            self.X = data.drop(labels=label_column_name, axis=1)

            # Filter the Label columns
            self.Y = data[label_column_name]  # Filter the Label columns

            self.logger_object.log(self.file_object,
                                   'Label Separation Successful. Exited the separate_label_feature method of the '
                                   'Preprocessor class')
            return self.X, self.Y

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in separate_label_feature method of the Preprocessor class.'
                                   ' Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Label Separation Unsuccessful. Exited the separate_label_feature method of the '
                                   'Preprocessor class')
            raise Exception()

    def dropUnnecessaryColumns(self, data, columnNameList):
        """
                        Method Name: is_null_present
                        Description: This method drops the unwanted columns as discussed in EDA section.

                        Written By: Rakesh Uikey
                        Version: 1.0
                        Revisions: None

        """
        self.logger_object.log(self.file_object, 'Entered into dropUnnecessaryColumns method of preprocessor class')
        try:
            data = data.drop(columnNameList, axis=1)

            self.logger_object.log(self.file_object, 'Dropping of columns successful!!')
            return data
        except Exception as e:
            self.logger_object.log(self.file_object, 'Unable to drops columns!!')
            self.logger_object.log(self.file_object, 'Error %s while dropping column' % e)
            raise Exception()

    def replaceInvalidValuesWithNull(self, data):
        """
                        Method Name: is_null_present
                        Description: This method replaces invalid values i.e. '?' with null, as discussed in EDA.

                        Written By: Rakesh Uikey
                        Version: 1.0
                        Revisions: None
        """

        self.logger_object.log(self.file_object, 'Entered into  replaceInvalidValuesWithNull method of the '
                                                 'Preprocessor class')
        try:
            for column in data.columns:
                count = data[column][data[column] == '?'].count()
                if count != 0:
                    data[column] = data[column].replace('?', np.nan)
            self.logger_object.log(self.file_object, 'Replacing Invalid values with Null is Successfully!!')
            return data
        except Exception as e:
            self.logger_object.log(self.file_object, 'Unable to replace Invalid values with Null is Successfully!!')
            raise e

    def is_null_present(self, data):
        """
                      Method Name: is_null_present
                      Description: This method checks whether there are null values present in the pandas Dataframe or not.
                      Output: Returns a Boolean Value. True if null values are present in the DataFrame, False if they are not present.
                      On Failure: Raise Exception

                      Written By: Rakesh Uikey
                      Version: 1.0
                      Revisions: None

        """
        self.logger_object.log(self.file_object, 'Entered the is_null_present method of the Preprocessor class')
        self.null_present = False
        try:
            self.null_counts = data.isna().sum()  # check for the count of null values per column
            for i in self.null_counts:
                if i > 0:
                    self.null_present = True
                    break
            if (self.null_present):  # write the logs to see which columns have null values
                dataframe_with_null = pd.DataFrame()
                dataframe_with_null['columns'] = data.columns
                dataframe_with_null['missing values count'] = np.asarray(data.isna().sum())
                dataframe_with_null.to_csv(
                    'preprocessing_data/null_values.csv')  # storing the null column information to file
            self.logger_object.log(self.file_object,
                                   'Finding missing values is a success.Data written to the null values file. Exited '
                                   'the is_null_present method of the Preprocessor class')
            return self.null_present

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in is_null_present method of the Preprocessor class. '
                                   'Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Finding missing values failed. Exited the is_null_present method of the '
                                   'Preprocessor class')
            raise Exception()

    def encodeCategoricalValues(self, data):
        """
                                Method Name: encodeCategoricalValues
                                Description: This method encodes all the categorical values in the training set.
                                Output: A Dataframe which has all the categorical values encoded.
                                On Failure: Raise Exception

                                Written By: Rakesh Uikey
                                Version: 1.0
                                Revisions: None
        """
        self.logger_object.log(self.file_object,
                               'Entered into encodeCategoricalValues method of the Preprocessor class')
        try:
            # We can map the categorical values like below:
            data['sex'] = data['sex'].map({'F': 0, 'M': 1})

            # except for 'Sex' column all the other columns with two categorical data have same value 'f' and 't'.
            # so instead of mapping individually, let's do a smarter work

            for column in data.columns:
                if len(data[column].unique()) == 2:
                    data[column] = data[column].map({'f': 0, 't': 1})

            # this will map all the rest of the columns as we require. Now there are handful of column left with more
            # than 2 categories. we will use get_dummies with that.


            encode = LabelEncoder().fit(data['field_30_'])

            data['Class'] = encode.transform(data['field_30_'])
            data = data.drop(['field_30_'], axis=1)

            # we will save the encoder as pickle to use when we do the prediction. We will need to decode the
            # predicted values back to original
            with open('EncoderPickle/enc.pickle', 'wb') as file:
                pickle.dump(encode, file)
            self.logger_object.log(self.file_object, 'Encoder model saved  successfully!!!')
            self.logger_object.log(self.file_object, 'Encoding of values is successful!!')

            return data

        except Exception as e:
            self.logger_object.log(self.file_object, 'Exception occurred : %s' + str(e))
            self.logger_object.log(self.file_object,
                                   'Fail to Encoding of values !!')
            raise Exception()

    def encodeCategoricalValuesPrediction(self, data):
        """
                                    Method Name: encodeCategoricalValuesPrediction
                                    Description: This method encodes all the categorical values in the prediction set.
                                    Output: A Dataframe which has all the categorical values encoded.
                                    On Failure: Raise Exception

                                    Written By: Rakesh Uikey
                                    Version: 1.0
                                    Revisions: None
        """

        # We can map the categorical values like below:
        data['sex'] = data['sex'].map({'F': 0, 'M': 1})
        cat_data = data.drop(['age', 't3', 'tt4', 't4u', 'fti', 'sex'], axis=1)
        # we do not want to encode values with int or float type
        # except for 'Sex' column all the other columns with two categorical data have same value 'f' and 't'.
        # so instead of mapping individually, let's do a smarter work
        for column in cat_data.columns:
            if (data[column].nunique()) == 1:
                if data[column].unique()[0] == 'f' or data[column].unique()[0] == 'F':
                    # map the variables same as we did in training i.e. if only 'f' comes map as 0 as
                    # done in training
                    data[column] = data[column].map({data[column].unique()[0]: 0})
                else:
                    data[column] = data[column].map({data[column].unique()[0]: 1})
            elif (data[column].nunique()) == 2:
                data[column] = data[column].map({'f': 0, 't': 1})

        return data

    def handleImbalanceDataset(self, X, Y):
        """
                            Method Name: handleImbalanceDataset
                            Description: This method handles the imbalance in the dataset by oversampling.
                            Output: A Dataframe which is balanced now.
                            On Failure: Raise Exception

                            Written By: Rakesh Uikey
                            Version: 1.0
                            Revisions: None
        """

        rdsmple = RandomOverSampler()
        x_sampled, y_sampled = rdsmple.fit_sample(X, Y)

        return x_sampled, y_sampled

    def impute_missing_values(self, data):
        """
                         Method Name: impute_missing_values
                         Description: This method replaces all the missing values in the Dataframe using KNN Imputer.
                         Output: A Dataframe which has all the missing values imputed.
                         On Failure: Raise Exception

                         Written By: Rakesh Uikey
                         Version: 1.0
                         Revisions: None
        """
        self.logger_object.log(self.file_object, 'Entered the impute_missing_values method of the Preprocessor class')
        self.data = data
        try:
            for column in data.columns:
                if (data[column].nunique()) == 1:
                    # map the variables same as we did in training i.e. if only 'f' comes map as 0 as done in training
                    if data[column].unique()[0] == 'f' or data[column].unique()[0] == 'F':
                        data[column] = data[column].map({data[column].unique()[0]: 0})

            imputer = KNNImputer(n_neighbors=3, weights='uniform', missing_values=np.nan)

            self.new_array = imputer.fit_transform(self.data)  # impute the missing values

            # convert the nd-array returned to the step above to a Dataframe
            # rounding the value because KNNImpute returns value between 0 and 1, but we need either 0 or 1
            self.new_data = pd.DataFrame(data=np.round(self.new_array), columns=self.data.columns)
            self.logger_object.log(self.file_object,
                                   'Imputing missing values Successful. Exited the impute_missing_values method of '
                                   'the Preprocessor class')
            return self.new_data

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in impute_missing_values method of the Preprocessor class. '
                                   'Exception message: ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Imputing missing values failed. Exited the impute_missing_values method of the '
                                   'Preprocessor class')
            raise Exception()

    def get_columns_with_zero_std_deviation(self, data):
        """
                                Method Name: get_columns_with_zero_std_deviation
                                Description: This method finds out the columns which have a standard deviation of zero.
                                Output: List of the columns with standard deviation of zero
                                On Failure: Raise Exception

                                Written By: Rakesh Uikey
                                Version: 1.0
                                Revisions: None
        """
        self.logger_object.log(self.file_object,
                               'Entered the get_columns_with_zero_std_deviation method of the Preprocessor class')
        self.columns = data.columns
        self.data_n = data.describe()
        self.col_to_drop = []
        try:
            for x in self.columns:
                if self.data_n[x]['std'] == 0:  # check if standard deviation is zero
                    self.col_to_drop.append(x)  # prepare the list of columns with standard deviation zero
            self.logger_object.log(self.file_object,
                                   'Column search for Standard Deviation of Zero Successful. Exited the '
                                   'get_columns_with_zero_std_deviation method of the Preprocessor class')
            return self.col_to_drop

        except Exception as e:
            self.logger_object.log(self.file_object,
                                   'Exception occurred in get_columns_with_zero_std_deviation method of the '
                                   'Preprocessor class. Exception message:  ' + str(e))
            self.logger_object.log(self.file_object,
                                   'Column search for Standard Deviation of Zero Failed. Exited the '
                                   'get_columns_with_zero_std_deviation method of the Preprocessor class')
            raise Exception()
