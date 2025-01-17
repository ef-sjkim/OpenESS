#-*- coding: utf-8 -*-
import numpy as np
import joblib

from sklearn.preprocessing import MinMaxScaler

import torch
from torch.utils.data import DataLoader, TensorDataset
from trainer.DeepAnt_trainer import DeepAntModel

class DeepAnt_pred:
    def __init__(self,
                 scaler_path:str = './model/deepant_scaler.pkl',
                 model_path:str = './model/deepant_model.pth'
                 ):
        self.__scaler = self.load_scaler(scaler_path)
        self.__model = self.load_model(model_path)
        
    def load_scaler(self, scaler_path):
        scaler = joblib.load(scaler_path)
        return scaler
        
    def load_model(self, model_path):
        
        checkpoint = torch.load(model_path)
        
        model = DeepAntModel(checkpoint['n_features'])
        model.load_state_dict(checkpoint['weights'])
        model = model.to_device(model, model.device)
        return model
        
    def load_dataset(self, data):
        
        time_index = data.index.values[np.arange(10,len(data)).reshape(-1,1)]
        data = self.__scaler.transform(data)
        
        
        
        
        
        X = data[np.arange(10)[None, :] + np.arange(data.shape[0]-10).reshape(-1,1)]
        y = data[np.arange(10,data.shape[0]).reshape(-1,1)]
     
        
        test_loader = DataLoader(
            
                        TensorDataset(
                            torch.tensor(X,dtype = torch.float32).permute(0,2,1),
                            torch.tensor(y, dtype = torch.float32).permute(0,2,1)
                            ),
                batch_size=1,shuffle = False, num_workers=0)
            
                
        return test_loader, time_index
    

        
    def anomaly_detection(self, test_loader):
        
        result = self.__model.testing(test_loader)    
        print('Done')
        return result
    
class DeepAnt_train:
    def __init__(self,
                 
                 batch_size:int,
                 n_epochs: int,
                 lr: float,
                 n_features:int = 1,
                 ):
        self.batch_size = batch_size
        self.n_epochs = n_epochs
        self.lr = lr
        self.n_features = n_features
        
        pass
    
    def fit_scaler(self, data):
        scaler = MinMaxScaler()
        data = scaler.fit_transform(data)
        self.save_scaler(scaler)
        return data
    @classmethod
    def save_scaler(cls, scaler):
        joblib.dump(scaler, './model/deepant_scaler.pkl')
        print('DeepAnt Scaler Saved to model/deepant_scaler.pkl')
        
        pass
    
    def load_dataset(self, data):
        
        train_data = data[:int(np.floor(.7 *  data.shape[0]))]
        val_data = data[int(np.floor(.7 *  data.shape[0])):int(np.floor(data.shape[0]))]
        
        
        X_train = train_data[np.arange(10)[None, :] + np.arange(train_data.shape[0]-10).reshape(-1,1)]
        y_train = train_data[np.arange(10,train_data.shape[0]).reshape(-1,1)]
        
        X_val = val_data[np.arange(10)[None, :] + np.arange(val_data.shape[0]-10).reshape(-1,1)]
        y_val = val_data[np.arange(10,val_data.shape[0]).reshape(-1,1)]
        
        train_loader = DataLoader(
            
                        TensorDataset(
                            torch.tensor(X_train,dtype = torch.float32).permute(0,2,1),
                            torch.tensor(y_train, dtype = torch.float32).permute(0,2,1)
                            ),
                batch_size=self.batch_size,shuffle = False, num_workers=0)
        val_loader = DataLoader(
            
                        TensorDataset(
                            torch.tensor(X_val,dtype = torch.float32).permute(0,2,1),
                            torch.tensor(y_val, dtype = torch.float32).permute(0,2,1)
                            ),
                batch_size=self.batch_size,shuffle = False, num_workers=0)
            
            
                
        return train_loader, val_loader
        
        
        
    
    
    def fit(self, train_loader, val_loader, lr, es_epochs):
        self.model = DeepAntModel(n_features=self.n_features)
        print(self.model)       
        
        self.model = self.model.to_device(self.model, self.model.device)
        
        history = self.model.fit(self.n_epochs, train_loader, val_loader, lr = lr, es_epochs= es_epochs)
        
        return history
    
    def save_model(self):
        
        torch.save({
            'n_features':self.n_features,
            'weights':self.model.state_dict()
        }, "./model/deepant_model.pth")
        print('DeepAnt Model Saved to model/deepant_model.pth')
        
        
    
    
    
    

       
    
    
    