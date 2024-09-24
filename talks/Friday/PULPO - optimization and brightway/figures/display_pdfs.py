import matplotlib.pyplot as plt
from ipywidgets import interact
from pdf2image import convert_from_path

def show_figure(index):
    pdf_path = 'figures/optimization_slideshow.pdf'
    figures = convert_from_path(pdf_path, dpi=600)  # Set DPI to 300 for better quality
    plt.figure(figsize=(8, 6))
    plt.imshow(figures[index])
    plt.axis('off')
    plt.show()

def show_all_figures():
    # Convert PDF pages to images with higher DPI for better quality
    pdf_path = 'figures/optimization_slideshow.pdf'
    figures = convert_from_path(pdf_path, dpi=600)  # Set DPI to 300 for better quality
    # Create a slider to interact with the figures
    interact(show_figure, index=(0, len(figures) - 1))