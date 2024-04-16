from torchvision.transforms import functional
from PIL import Image
import torch
from torchvision import transforms
import torch.nn.functional as F
import numpy as np
from sklearn.cluster import DBSCAN

class PathFinder:
    def __init__(self, image_size=(200, 200), sobel_magnitude_threshold=0.25, sobel_y_threshold=120, eps=1, min_samples=20, pointB_y_offset=50) -> None:
        self.image_size = image_size
        self.__init_kernel()
        self.magnitude_threshold = sobel_magnitude_threshold
        self.y_threshold = sobel_y_threshold
        self.eps = eps
        self.min_samples = min_samples
        self.y_offset = pointB_y_offset


    def __init_kernel(self, vert_values=[3., 6.], horz_values=[1., 2.]):
        # Définir les noyaux Sobel pour les dérivées horizontales et verticales
        sobel_kernel_x = torch.tensor([[-vert_values[0], 0., vert_values[0]],
                                       [-vert_values[1], 0., vert_values[1]],
                                       [-vert_values[0], 0., vert_values[0]]])

        sobel_kernel_y = torch.tensor([[-horz_values[0], -horz_values[1], -horz_values[0]],
                                       [0., 0., 0.],
                                       [horz_values[0], horz_values[1], horz_values[0]]])
        
        # Ces noyaux doivent être étendus pour s'adapter aux dimensions de l'image [batch_size, channels, height, width] out_channels, in_channels, height, width]
        sobel_kernel_x = sobel_kernel_x.view((1, 1, 3, 3))
        sobel_kernel_y = sobel_kernel_y.view((1, 1, 3, 3))

        # Vérifiez si CUDA est disponible et définissez le périphérique en conséquence
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Convertir les noyaux en types de données adaptés pour les calculs de convolution
        self.sobel_kernel_x = sobel_kernel_x.to(self.device, dtype=torch.float32)
        self.sobel_kernel_y = sobel_kernel_y.to(self.device, dtype=torch.float32)


    def detect_line(self, image) -> tuple:
        """
        Détecte une ligne dans une image en utilisant un filtre de Sobel ainsi que DBSCAN pour regrouper les points de contour. Retourne les coordonnées
        des points A et B sur la ligne. Le point A est placé tout en bas de l'image (sous le drone) tandis que le point B est placé à une certaine hauteur
        (y_offset) au-dessus du point A.
        :param image: Image à traiter
        """
        # Convertir l'image en PIL si ce n'est pas déjà le cas
        if not isinstance(image, Image.Image):
            image = Image.fromarray(image[0])

        # Appliquer un filtre de Sobel pour détecter les contours
        sobel_image = self.__sobel_filter(image)

        # Détecter les points A et B de la ligne
        point_A, point_B = self.__compute_points_A_B(sobel_image)

        return (point_A[0], point_A[1], point_B[0], point_B[1])
    

    def __sobel_filter(self, preprocessed_image):
        """
        Applique un filtre de Sobel sur une image pour détecter les contours.
        :param preprocessed_image: Image prétraitée à laquelle appliquer le filtre de Sobel
        """
        # Convertir l'image en tenseur PyTorch
        transform = transforms.ToTensor()
        image_tensor = transform(preprocessed_image).to(self.device)
    
        # Ajouter des dimensions de batch et de canal pour correspondre à la forme [B, C, H, W]
        image_tensor = image_tensor.unsqueeze(0)

        # Appliquer le filtre de Sobel sur l'image tensorielle
        Gx = F.conv2d(image_tensor, self.sobel_kernel_x, padding=1)
        Gy = F.conv2d(image_tensor, self.sobel_kernel_y, padding=1)

        # Calculer la magnitude du gradient
        sobel_magnitude = torch.sqrt(Gx**2 + Gy**2)

        # Appliquer un seuillage pour binariser l'image
        sobel_binary = torch.where(sobel_magnitude > self.magnitude_threshold, torch.tensor(1.0), torch.tensor(0.0))

        # Rendre les pixels dont la coordonnée y est supérieure à y_threshold noirs
        sobel_binary[:, :, :self.y_threshold:, :] = 0.0

        # Créer un masque pour fixer les pixels tout à gauche, tout à droite et tout en bas de l'image en noir
        sobel_binary[:, :, :, :1] = 0.0  # Fixer les pixels tout à gauche de l'image
        sobel_binary[:, :, :, -1:] = 0.0  # Fixer les pixels tout à droite de l'image
        sobel_binary[:, :, -1:, :] = 0.0  # Fixer les pixels tout en bas de l'image
    
        # Convertir le gradient en image PIL pour l'affichage
        sobel_magnitude_image = transforms.ToPILImage()(sobel_binary.squeeze(0))
    
        return sobel_magnitude_image
    

    def __compute_point(self, points, y_min, y_max, y_true):
        """
        Calcule les coordonnées d'un point en prenant en compte les points voisons pour déterminer le centre en X. La coordonnée Y est placé à y_true.
        :param points: Ensemble de points pour lesquels calculer le centre
        :param y_min: Coordonnée y minimale pour le calcul du centre
        :param y_max: Coordonnée y maximale pour le calcul du centre
        :param y_true: Coordonnée y à laquelle le centre doit être placé
        """
        return int(np.array([point for point in points if y_min <= point[1] <= y_max]).mean(axis=0)[0]), y_true

    
    def __compute_points_A_B(self, sobel_image):
        """
        Détecte les lignes dans une image binarisée en utilisant un algorithme de clustering DBSCAN pour regrouper les points de contour.
        :param sobel_image: Image binarisée à traiter
        """
        # Créer une liste pour stocker les points de contour
        points = []
        for x in range(sobel_image.size[0]):
            for y in range(sobel_image.size[1]):
                if sobel_image.getpixel((x, y)) == 255:
                    points.append((x, y))

        # Utilisation de DBSCAN pour détecter les lignes
        dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples)
        clusters = dbscan.fit_predict(points)

        # Récupère les clusters et compte le nombre de points dans chaque cluster
        line_points = []
        unique, counts = np.unique(clusters, return_counts=True)
        for label in unique:
            if label == unique[np.argmax(counts)]: # On ne garde que le cluster le plus grand
                cluster_points = np.array(points)[clusters == label]
                line_points.append(cluster_points)

        # Calculer les points de début et de fin de la ligne
        point_A = self.__compute_point(cluster_points, 180, 195, 200)

        min_value_y = cluster_points.min(axis=0)[1]
        y_B = 200 - self.y_offset
        if y_B < min_value_y:
            y_B = min_value_y
            print("Warning: y_max - y_offset < y_min. y_offset is set to y_min")

        point_B = self.__compute_point(cluster_points, y_B - 5, y_B + 5, y_B)

        return point_A, point_B
    
def init():
    return PathFinder()