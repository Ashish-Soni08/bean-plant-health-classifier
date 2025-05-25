import gradio as gr

from PIL import Image

import spaces

from typing import Dict
import torch
from transformers import ViTImageProcessor, AutoFeatureExtractor, AutoModelForImageClassification

image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")

extractor = AutoFeatureExtractor.from_pretrained("saved_model_files")
model = AutoModelForImageClassification.from_pretrained("saved_model_files")

labels = ['angular_leaf_spot', 'bean_rust', 'healthy'] 

@spaces.GPU(duration=500)
def classify(image: Image.Image) -> Dict[str, float]:
    """
    Classify an image of a bean plant leaf into one of several health categories.

    Args:
        image (Image.Image): The input image of the bean leaf to be classified.

    Returns:
        Dict[str, float]: A dictionary where the keys are the health labels 
                          (e.g., 'angular_leaf_spot', 'bean_rust', 'healthy') and 
                          the values are the confidence scores for each label.
    """
    features = image_processor(image, return_tensors='pt')
    logits = model(features["pixel_values"])[-1]
    probability = torch.nn.functional.softmax(logits, dim=-1)
    probs = probability[0].detach().numpy()
    confidences = {label: float(probs[i]) for i, label in enumerate(labels)} 
    return confidences

####### GRADIO APP #######
title = """<h1 id="title">Bean plant health predictor through images of leaves using ViT image classifier</h1>"""

description = """
Problem Statement: A farming company that is having issues with diseases affecting their bean plants. The farmers have to constantly monitor the leaves of the plants so that they can immediately treat the leaves if they show any signs of disease. 
We are asked to build a machine learning-based app they can deploy on a drone to quickly identify diseased plants.


Solution: Building a Leaf Classification App that focuses on image classification to quickly identify diseased plants.

- The Dataset used for finetuning the model [Beans](https://huggingface.co/datasets/beans). 
- The model used for classifying the images [Vision Transformer (base-sized model)](https://huggingface.co/google/vit-base-patch16-224).
"""

css = '''
h1#title {
  text-align: center;
}
'''
theme = gr.themes.Soft()
demo = gr.Blocks(css=css, theme=theme)

with demo:
  gr.Markdown(title)
  gr.Markdown(description)
  interface =  gr.Interface(fn=classify, 
                            inputs="image",
                            outputs="label",
                           examples="images")

demo.launch()