"""
You need to implement all four functions in this file and also put your team info as a variable
Then you should submit the python file with your model class, the state_dict, and this file
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

# import your model class
# import ...
from project_models import *

# Put your transform function here, we will use it for our dataloader
# For bounding boxes task
def get_transform_task1(): 
    return torchvision.transforms.ToTensor()
# For road map task
def get_transform_task2(): 
    return torchvision.transforms.ToTensor()

class ModelLoader():
    # Fill the information for your team
    team_name = 'Leafy Green Team'
    team_number = 2
    round_number = 2
    team_member = ['ak7288','mrf444']
    contact_email = '@nyu.edu'

    def __init__(self, model_file='models'):
        # You should 
        #       1. create the model object
        #       2. load your state_dict
        #       3. call cuda()
        # self.model = ...
        # 
        #call cuda()
        cuda = torch.cuda.is_available()
        self.device = torch.device("cuda:0" if cuda else "cpu")

        #load UNet for roadmap predictions
        self.unet_roadmap_model = UNet(num_classes=2, semi_supervised=False)
        self.unet_roadmap_model.load_state_dict(torch.load(model_file)['unet_roadmap']) #roadmaps
        self.unet_roadmap_model.to(self.device)
        
        #load UNet for bounding box predictions
        #feature extractor
        self.feature_extractor = Unsupervised_Model_wo_convtrans()
        self.feature_extractor.linear2 = Identity()
        self.feature_extractor.load_state_dict(torch.load(model_file)['feature_extractor_unfrozen']) #already double
        self.feature_extractor.to(self.device)
        
        #semi_supervised UNet
        self.unet_semisupervised = UNet(num_classes=2,semi_supervised=True)
        self.unet_semisupervised.load_state_dict(torch.load(model_file)['semi_supervised_unfrozen']) #already double
        self.unet_semisupervised.to(self.device)

    def get_bounding_boxes(self, samples):
        # samples is a cuda tensor with size [batch_size, 6, 3, 256, 306]
        # You need to return a tuple with size 'batch_size' and each element is a cuda tensor [N, 2, 4]
        # where N is the number of object

        return torch.rand(1, 15, 2, 4) * 10

    def get_binary_road_map(self, samples):
        # samples is a cuda tensor with size [batch_size, 6, 3, 256, 306]
        # You need to return a cuda tensor with size [batch_size, 800, 800] 
        model_input = torch.mean(samples,axis=1)

        # Send data to device
        model_input = model_input.to(self.device)
        
        # Pass data through model
        output = self.unet_roadmap_model(model_input)
        output = F.log_softmax(output,dim=1)
        
        # Get predictions (indices) from the model for each data point
        model_preds = output.data.max(1,keepdim=True)[1]
        
        return model_preds.squeeze(1) #[batch_size, 800, 800]
