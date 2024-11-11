# CV_Azat.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

label_map = {
    'im_Metaplastic': 0,
    'im_Dyskeratotic': 1,
    'im_Superficial-Intermediate': 2,
    'im_Parabasal': 3,
    'im_Koilocytotic': 4
}
reverse_label_map = {v: k for k, v in label_map.items()}

device = torch.device('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f'Устройство: {device}')

model = models.resnet34(pretrained=False)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, len(label_map))
model = model.to(device)

model_path = 'best_cancer_classification_model.pth'
if not os.path.exists(model_path):
    logger.error(f"Файл модели {model_path} не найден.")
    raise FileNotFoundError(f"Файл модели {model_path} не найден.")

state_dict = torch.load(model_path, map_location=device)
model.load_state_dict(state_dict)
model.eval()  # Установить модель в режим оценки
logger.info("Модель успешно загружена и установлена в режим оценки.")

test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_image(image_path, transform=None):
    try:
        image = Image.open(image_path).convert('RGB')
        if transform:
            image = transform(image)
        logger.info(f"Изображение {image_path} успешно загружено и преобразовано.")
        return image
    except Exception as e:
        logger.exception(f"Ошибка при загрузке изображения {image_path}: {e}")
        raise

def predict_image(model, image, device, reverse_label_map):
    """
    Функция для предсказания типа рака на изображении клетки.
    Принимает модель, изображение (предобработанное), устройство и обратную карту меток.
    Возвращает предсказанный класс и уверенность.
    """
    try:
        model.eval()
        image = image.unsqueeze(0)
        image = image.to(device)

        with torch.no_grad():
            outputs = model(image)
            probabilities = F.softmax(outputs, dim=1)
            confidence, preds = torch.max(probabilities, 1)

        predicted_class = reverse_label_map[preds.item()]
        confidence_score = confidence.item()

        logger.info(f"Предсказанный класс: {predicted_class}, Уверенность: {confidence_score:.2f}")

        return predicted_class, confidence_score
    except Exception as e:
        logger.exception("Ошибка при предсказании изображения.")
        raise
