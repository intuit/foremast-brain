from __future__ import print_function
import mxnet as mx
from mxnet import nd, autograd
from mxnet import gluon
import numpy as np
import warnings; warnings.simplefilter('ignore')

L = gluon.loss.L2Loss()
ctx=mx.cpu()


############LSTM##################


def createModel(ctx, features_size=1, window_size=1, learning_rate = 0.01, drop_out = 0.35):
    model = mx.gluon.nn.Sequential()
    with model.name_scope():
        model.add(mx.gluon.rnn.LSTM(window_size, dropout=drop_out))
        model.add(mx.gluon.rnn.LSTM(features_size))
    model.collect_params().initialize(mx.init.Xavier(), ctx=ctx)
    trainer = gluon.Trainer(model.collect_params(), 'adam', {'learning_rate': learning_rate})
    return model, trainer


def evaluate_accuracy(data_iterator, model, L, window =1, features =1):
    loss_avg = 0.
    for i, data in enumerate(data_iterator):
        data = data.as_in_context(ctx).reshape((-1, window, features))
        label = data
        output = model(data)
        loss = L(output, label)
        loss_avg = loss_avg*i/(i+1) + nd.mean(loss).asscalar()/(i+1)
    return loss_avg



def trainModel(traindata, testdata, model, trainer, ctx, window=1, features=1, epochs = 25, batchsize=128):
    all_train_mse = []
    all_test_mse = []
    for e in range(epochs):
        for i, data in enumerate(traindata):
            data = data.as_in_context(ctx).reshape((-1, window, features))
            label = data
            with autograd.record():
                output = model(data)
                loss = L(output, label)
            loss.backward()
            trainer.step(batchsize)    
        train_mse = evaluate_accuracy(traindata, model, L)
        test_mse = evaluate_accuracy(testdata, model, L)
        all_train_mse.append(train_mse)
        all_test_mse.append(test_mse)
    return all_train_mse , all_test_mse


def predict(to_predict, L, model,features = 1):
    predictions = []
    for i, data in enumerate(to_predict):
        data = data.as_in_context(ctx).reshape((-1,features,1))
        input = data
        out = model(input)
        prediction = L(out, input).asnumpy().flatten()
        predictions = np.append(predictions, prediction)
    return predictions

def load_and_predict(dataset,L, model, batch_size=128, features =1):
    dataset_data = mx.gluon.data.DataLoader(dataset, batch_size, shuffle=False)
    dataset_predictions = predict(dataset_data, L,model, features)
    return dataset_predictions


def calculateUpperLowerBound(predictions , zvalue = 2):
    mean =np.mean(predictions) 
    std = np.std(predictions)
    upper =  mean + zvalue*std
    lower = mean - zvalue*std
    return upper, lower

def calculateAnomaly(predictions, threshold):
    anomaly = list(map(lambda v: v > threshold, predictions))
    return anomaly


def load(dataset, batch_size=128):
    return mx.gluon.data.DataLoader(dataset, batch_size, shuffle=False)






