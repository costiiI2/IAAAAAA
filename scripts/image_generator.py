import numpy as np
import cv2
import json

X = 1000
N = 100
Y_HEIGHT = 50
points_data = []

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt

# Définir les noyaux Sobel pour les dérivées horizontales et verticales
vert_values = [3., 6.]
sobel_kernel_x = torch.tensor([[-vert_values[0], 0., vert_values[0]],
                               [-vert_values[1], 0., vert_values[1]],
                               [-vert_values[0], 0., vert_values[0]]])

horz_values = [1., 2.]
sobel_kernel_y = torch.tensor([[-horz_values[0], -horz_values[1], -horz_values[0]],
                               [0., 0., 0.],
                               [horz_values[0], horz_values[1], horz_values[0]]])

# Ces noyaux doivent être étendus pour s'adapter aux dimensions de l'image [batch_size, channels, height, width]
# [out_channels, in_channels, height, width]
sobel_kernel_x = sobel_kernel_x.view((1, 1, 3, 3))
sobel_kernel_y = sobel_kernel_y.view((1, 1, 3, 3))

# Vérifiez si CUDA est disponible et définissez le périphérique en conséquence
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Convertir les noyaux en types de données adaptés pour les calculs de convolution
sobel_kernel_x = sobel_kernel_x.to(device, dtype=torch.float32)
sobel_kernel_y = sobel_kernel_y.to(device, dtype=torch.float32)



# Fonction pour appliquer le filtre Sobel à une image
def sobel_filter(img_path):
    # Charger l'image en utilisant Pillow et la convertir en tenseur PyTorch
    image = Image.open(img_path).convert("L")

    transform = transforms.ToTensor()
    image_tensor = transform(image).to(device)
    
    # Ajouter des dimensions de batch et de canal pour correspondre à la forme [B, C, H, W]
    image_tensor = image_tensor.unsqueeze(0)

    # Appliquer le filtre de Sobel sur l'image tensorielle
    Gx = F.conv2d(image_tensor, sobel_kernel_x, padding=1)
    Gy = F.conv2d(image_tensor, sobel_kernel_y, padding=1)

    # Calculer la magnitude du gradient
    sobel_magnitude = torch.sqrt(Gx**2 + Gy**2)
    
    # Convertir le gradient en image PIL pour l'affichage
    sobel_magnitude_image = transforms.ToPILImage()(sobel_magnitude.squeeze(0))
    
    return sobel_magnitude_image

# Generate and save 10 images
for i in range(X):
    original_image = np.zeros((200, 200), dtype=np.uint8)
    
    # Generate random points for the line
    # bottom point
    x1 = np.random.randint(10, 190)
    y1 = 200 
    # top point
    x2 = np.random.randint(10, 190)
    y2 = 0
    
    # Calculate midpoint
    mx = (x1 + x2) // 2 + np.random.randint(-50, 50)
    if mx < 10:
        mx = 10
    elif mx > 190:
        mx = 190
    my = np.random.randint(50, 150)  # Ensure midpoint is above both ends
    
    # Draw the line in two segments
    cv2.line(original_image, (x1, y1), (mx, my), 255, 10)
    cv2.line(original_image, (mx, my), (x2, y2), 255, 10)

    # Save the original image
    cv2.imwrite(f"images/og.png", original_image)
    
  # Apply Sobel filter to the original image
    sobel_image = np.array(sobel_filter(f"images/og.png"))

    # Save the filtered image
    if i < N:
        #find a point on the line a Y = Y_HEIGHT
        x3 = int((x1 + mx) / 2)
        cv2.imwrite(f"test_img/{i}__{x1}_0_{x3}_{Y_HEIGHT}.png", sobel_image.astype(np.uint8))
    else:
        points_data.append({"image_id": i, "points": [(x1, 0), (mx, 200-my)]})
        cv2.imwrite(f"images/{i}.png", sobel_image.astype(np.uint8))  # Ensure the data type is uint8


# Save the points data in a JSON file
with open("points_data.json", "w") as f:
    json.dump(points_data, f)
