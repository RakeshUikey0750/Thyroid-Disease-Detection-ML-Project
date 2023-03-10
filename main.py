import json
from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import Response
import os
from flask_cors import CORS, cross_origin
from prediction_Validation_Insertion import pred_validation
from trainingModel import trainModel
from training_Validation_Insertion import train_validation
import flask_monitoringdashboard as dashboard
from predictFromModel import prediction
from predictFromModelFor_single_record import predicting_single_rec

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
dashboard.bind(app)
CORS(app)


@app.route("/", methods=['GET', 'POST'])
@cross_origin()
def home():
    return render_template('home.html')


@app.route("/predict4_1", methods=['GET', 'POST'])
@cross_origin()
def predicton4_1():
    return render_template('prediction4_1.html')


@app.route("/predict", methods=['POST'])
@cross_origin()
def predict():
    if request.method == "POST":
        try:
            if request.form:
                data_req = dict(request.form)
                data = data_req.values()
                data = [list(data)]
                pred = predicting_single_rec(data)

                # predicting the output
                result = pred.predictionFromModel()
                return render_template("result.html", result=result[0])
            else:
                return "none"
        except Exception as e:
            error = {'error': e}
            return render_template("404.html", error=error)
    else:
        return render_template('404.html', error="Something went wrong!! Try again.")


@app.route("/predict_bulk", methods=['POST'])
@cross_origin()
def predictRouteClient():
    try:
        if request.json is not None:
            path = request.json['filepath']

            pred_val = pred_validation(path)  # object initialization

            pred_val.prediction_validation()  # calling the prediction_validation function

            pred = prediction(path)  # object initialization

            # predicting for dataset present in database
            path = pred.predictionFromModel()
            return Response("Prediction File created at !!! " + str(path))

        elif request.form is not None:

            path = request.form['filepath']

            pred_val = pred_validation(path)  # object initialization

            pred_val.prediction_validation()  # calling the prediction_validation function

            pred = prediction(path)  # object initialization

            # predicting for dataset present in database
            path = pred.predictionFromModel()
            return Response("Prediction File created at !!! " + str(path))
        else:
            print('Nothing Matched')

    except ValueError:
        return Response("Error Occurred! %s" % ValueError)
    except KeyError:
        return Response("Error Occurred! %s" % KeyError)
    except Exception as e:
        return Response("Error Occurred! %s" % e)


@app.route("/train", methods=['POST'])
@cross_origin()
def trainRouteClient():
    try:
        if request.json['filepath'] is not None:
            path = request.json['filepath']
            train_valObj = train_validation(path)  # object initialization

            train_valObj.train_validation()  # calling the training_validation function

            trainModelObj = trainModel()  # object initialization
            trainModelObj.trainingModel()  # training the model for the files in the table

    except ValueError:

        return Response("Error Occurred! %s" % ValueError)

    except KeyError:

        return Response("Error Occurred! %s" % KeyError)

    except Exception as e:

        return Response("Error Occurred! %s" % e)
    return Response("Training successful!!")


port = int(os.getenv("PORT", 5000))
if __name__ == "__main__":
    host = '0.0.0.0'
    # port = 5000
    httpd = simple_server.make_server(host, port, app)
    # print("Serving on %s %d" % (host, port))
    httpd.serve_forever()
