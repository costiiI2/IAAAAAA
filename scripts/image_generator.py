import numpy as np
import cv2
import json

X = 1000
N = 100
points_data = []

# Generate and save 10 images
for i in range(X):
    image = np.zeros((200, 200), dtype=np.uint8)
    
    # Generate random points for the line
    #bottom point
    x1 = np.random.randint(10, 190)
    y1 = 200 
    #top point
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
    cv2.line(image, (x1, y1), (mx, my), 255, 10)
    cv2.line(image, (mx, my), (x2, y2), 255, 10)

    #sobel the img
    
    
    # Save the image
    if(i < N):
        cv2.imwrite(f"test_img/{i}__{x1}_0.png", image)
    else:
        points_data.append({"image_id": i, "points": [(x1, 0), (mx, 200-my)]})
        cv2.imwrite(f"images/{i}.png", image)

# Save the points data in a JSON file
with open("points_data.json", "w") as f:
    json.dump(points_data, f)
