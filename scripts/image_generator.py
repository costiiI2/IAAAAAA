import numpy as np
import cv2

X = 100


def generate_image():
    image = np.zeros((200, 200), dtype=np.uint8)
    
    # Generate random points for the line
    x1 = np.random.randint(0, 200)
    y1 = 200
    x2 = np.random.randint(0, 200)
    y2 = 0
    
    # Calculate midpoint
    mx = (x1 + x2) // 2
    my = np.random.randint(100, 200)  # Ensure midpoint is above both ends
    
    # Draw the line in two segments
    cv2.line(image, (x1, y1), (mx, my), 255, 10)
    cv2.line(image, (mx, my), (x2, y2), 255, 10)

    return image

# Generate and save 10 images
for i in range(X):
    image = generate_image()
    cv2.imwrite(f"images/{i}.png", image)

