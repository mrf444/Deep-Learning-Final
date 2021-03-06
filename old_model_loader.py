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
def get_transform(): 
    return torchvision.transforms.ToTensor()

class ModelLoader():
    # Fill the information for your team
    team_name = 'Leafy Green Team'
    round_number = 1
    team_member = ['ak7288','mrf444']
    contact_email = '@nyu.edu'

    def __init__(self, model_file='UNet-UNet_bb'):
        # You should 
        #       1. create the model object
        #       2. load your state_dict
        #       3. call cuda()
        # self.model = ...
        # 
        # Define model, load from saved trained model, and sent to device

        #call cuda()
        cuda = torch.cuda.is_available()
        self.device = torch.device("cuda:0" if cuda else "cpu")

        #load UNet for roadmap predictions
        self.unet_roadmap_model = UNet(num_classes=2)
        self.unet_roadmap_model.load_state_dict(torch.load(model_file)['UNet']) #roadmaps
        self.unet_roadmap_model.to(self.device)
        
        #load UNet for bounding box predictions
        self.unet_bb_model = UNet(num_classes=2)
        self.unet_bb_model.load_state_dict(torch.load(model_file)['UNet_bb'])
        self.unet_bb_model.load_state_dict(torch.load(model_file))#bounding box
        self.unet_bb_model.to(self.device)

    def get_bounding_boxes(self, samples):
        # samples is a cuda tensor with size [batch_size, 6, 3, 256, 306]
        # You need to return a tuple with size 'batch_size' and each element is a cuda tensor [N, 2, 4]
        # where N is the number of object
        
        #averaged input
        model_input = torch.mean(samples,axis=1)

        # Send data and target to device
        model_input = model_input.to(self.device)

        # Pass data through model
        output = self.unet_bb_model(model_input) #returns [batch_size,2,800,800]
        output = F.softmax(output,dim=1) #[batch_size,2,800,800]
        
        #threshold output
        output = output.squeeze(0) #[2,800,800]
        model_preds = 1*(output[1] > 0.1)
        
        return get_bboxes_from_output(model_preds).unsqueeze(0)

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
