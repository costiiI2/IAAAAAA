import numpy as np
import cv2
import json
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Load the data from JSON file
with open("points_data.json", "r") as f:
    points_data = json.load(f)

# Prepare the dataset
X = []  # Features (images)
y = []  # Target (x1, y1) points

for data in points_data:
    image = cv2.imread(f"images/{data['image_id']}.png", cv2.IMREAD_GRAYSCALE)
    X.append(image.flatten())  # Flatten the image
    y.append(data['points'][0])  # Take the bottom point

X = np.array(X)
y = np.array(y)

# Split the dataset into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_val)
mse = mean_squared_error(y_val, y_pred)
print("Mean Squared Error:", mse)

# Now you can use this trained model to predict the (x1, y1) point from new images
# For example:
# Load  new images from disk
import glob

for i in range(10):
    filenames = glob.glob(f"test_img/{i}__*.png")
    for filename in filenames:
        new_image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        if new_image is None:
            print("Error: Unable to read image", filename)
            continue
        new_image_flattened = new_image.flatten()

        # Predict the (x1, y1) point
        predicted_point = model.predict([new_image_flattened])[0]
        print(f"Predicted Point for image {filename}:", predicted_point)

new_image = cv2.imread("test_img/ss.png", cv2.IMREAD_GRAYSCALE)
new_image_flattened = new_image.flatten()
predicted_point = model.predict([new_image_flattened])[0]
print(f"Predicted Point for image test_img/0__10_0.png:", predicted_point)



