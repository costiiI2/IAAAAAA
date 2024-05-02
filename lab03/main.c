#include <stdio.h>
#include <string.h>

// Structure représentant une image
struct {
    int* data;
    size_t height;
    size_t width;
} typedef Image;

/*
Fonction permettant de redimentionner une image en gardant les proportions de l'image originale.
    - Prend en paramètres la structure de l'image originale et la structure dans laquelle l'image sera redimensionnée
    - Retourne 0 si l'opération s'est bien déroulée, -1 sinon
*/
int crop_image(const Image* original, Image* cropped) {
    // Vérifie que les entrées ne soient pas nulles
    if (original == NULL || cropped == NULL) {
        return -1;
    }
    if (original->data == NULL || cropped->data == NULL) {
        return -1;
    }

    // Vérifie que les dimensions de l'image redimensionnée soient plus petites que celles de l'image originale
    if (cropped->height > original->height || cropped->width > original->width) {
        return -1;
    }

    // Calcule l'offset pour centrer l'image redimensionnée (si résultat impair, arrondi à l'inférieur)
    size_t left_offset = (size_t) (original->width - cropped->width) / 2;

    // Calcule l'offset pour placer l'image redimensionnée en bas de l'image originale
    size_t top_offset = (size_t) (original->height - cropped->height);

    // Copie uniquement les pixels nécessaires de l'image originale vers l'image redimensionnée (recadrage centrée en bas de l'image originale)
    // (memcpy copie les pixels de l'image originalle en ométant les pixels de l'image originale qui sont dans les offsets calculés)
    for (size_t i = 0; i < cropped->height; i++) {
        memcpy(cropped->data + i * cropped->width, original->data + (i + top_offset) * original->width + left_offset, cropped->width * sizeof(int));
    }

    return 0;
}

void print_image(Image image) {
    for (size_t line = 0; line < image.height; line++) {
        for (size_t column = 0; column < image.width; column++) {
            printf("%d ", image.data[line * image.width + column]);
        }
        printf("\n");
    }
}

int main()
{
    Image baseImage = { .data = (int[]) {1, 2, 3, 4, 5,
                                         6, 7, 8, 9, 10,
                                         11, 12, 13, 14, 15,
                                         16, 17, 18, 19, 20,
                                         21, 22, 23, 24, 25},
                        .height = 5,
                        .width = 5 };

    printf("Image de base:\n");
    print_image(baseImage);

    printf("\n");

    Image croppedImage = { .data = (int[]) {0, 0, 0,
                                            0, 0, 0,
                                            0, 0, 0},
                           .height = 3,
                           .width = 3 };

    crop_image(&baseImage, &croppedImage);

    printf("Image recadree:\n");
    print_image(croppedImage);

    return 0;
}