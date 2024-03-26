import numpy as np
import cv2

X = 10
gap = 30  # Fixed gap between the lines

def generate_image():
        image = np.zeros((200, 200), dtype=np.uint8)
        
        # Randomly generate the starting point at the bottom for the first line
        x1 = np.random.randint(0, 200)
        y1 = 200
        
        # Randomly generate the second point above the first point for the first line
        x2 = np.random.randint(0, 200)
        y2 = np.random.randint(0, y1)  
        
        # Randomly generate the third point above the second point but not in the same direction for the first line
        x3 = np.random.randint(0, 200)
        y3 = np.random.randint(0, y2)
        
        # Draw the first line
        cv2.line(image, (x1, y1), (x2, y2), 255, 1)
        cv2.line(image, (x2, y2), (x3, y3), 255, 1)
        
        # the starting point of the second line is offset by the gap
        x1 += gap
        #the second point is offset by the gap and adjusted depending on the side of the first line
        x2 += gap
        y2 = y1 - y2
        #the third point is offset by the gap and adjusted depending on the side of the second line
        x3 += gap
        y3 = y2 - y3
        # Draw the second line
        cv2.line(image, (x1, y1), (x2, y2), 255, 1)
        cv2.line(image, (x2, y2), (x3, y3), 255, 1)
    
        return image

for i in range(X):
    image = generate_image()
    cv2.imwrite(f"images/{i}.png", image)
