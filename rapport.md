\topmargin = -30pt
\textheight = 625pt

\center

# **Lab 2 - Following a line**

\hfill\break

\hfill\break

Département: **TIC**

Unité d'enseignement: **IAA**

\hfill\break

\hfill\break

\hfill\break

\hfill\break

\hfill\break

\hfill\break

\hfill\break

\hfill\break

\raggedright

Author (s):

- **CECCHET Costantino**
- **ROSAT Cedric**

Professor (s):

- **YANN Thoma**
- **ZAPATER Marina**

Assistant:

- **AKEDDAR Mehdi**
- **CHACUN Guillaume**
- **RIEDER Thomas**

Date:

- **26/03/2024**

\pagebreak

\hfill\break

\hfill\break

\center

*\[Page de mise en page, laissée vide par intention\]*

\raggedright

\pagebreak

## **Introduction**

For this laboratory we have to code an algorithm that would allow the drone to detect a line on an image.

This image is taken by the drone and it's a grey scale image[1,200,200].

The output of the algorithm should be a 2D directional vector coresponding to the direction of the line.

## **Dataset creation**

We had to create a dataset to test our algorithm.

We did by manually taking pictures with the drone of a white line on a table with different light conditions.

We took 25 pictures in total.

We need a lot more pictures to train our model, so we generated more pictures using a simple line on a black canvas generated using python.

### **Image generation using python**


#### **Straight lines**
we create images starting from the bottom and going upwards the direction must be random

```python
import numpy as np
import cv2

X = 10
def generate_image():
        image = np.zeros((200, 200), dtype=np.uint8)
        x1 = np.random.randint(0, 200)
        y1 = 200
        x2 = np.random.randint(0, 200)
        y2 = 0
        cv2.line(image, (x1, y1), (x2, y2), 255, 1)

        return image

for i in range(X):
        image = generate_image()
        cv2.imwrite(f"images/{i}.png", image)

```

With this code we generated X images.

this will allow us to train our model on straight lines.

#### **Curved lines**

We also generated images with curved lines.

```python

import numpy as np
import cv2

X = 10
def generate_image():
        image = np.zeros((200, 200), dtype=np.uint8)
        x1 = np.random.randint(0, 200)
        y1 = 200
        x2 = np.random.randint(0, 200)
        y2 = 0
        cv2.line(image, (x1, y1), (x2, y2), 255, 1)

        return image

for i in range(X):
        image = generate_image()
        cv2.imwrite(f"images/{i}.png", image)

```




## **Algorithm**

Our algorithm need to stick to this template:

```python
# init() -> your PathFinder object to import the model with weights
# detect_line(image: Array[float, shape=[1, 200, 200]]) -> Tuple[Ax: float, Ay: float, Bx: float, By: float]


from lab2 import init
pathfinder = init()
points = [pathfinder.detect_line(image) for image in images]
```

Meaning that we need to implement the function `get_direction` that takes an image as input and returns a 2D directional vector.

## **usefull commands**


### **Flash the drone stm32**
```bash
make
cfloader flash build/cf2.bin stm32-fw -w radio://0/80/2M/E7E7E7E718
```

### **source and flash the gap sdk**


```bash
source ~/projects/gap_sdk/sdk_env/bin/activate
source ~/projects/gap_sdk/configs/ai_deck.sh
make build image flash
```