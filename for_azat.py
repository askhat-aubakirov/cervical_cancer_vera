# for_azat.py
import joblib  # to load the model
import pandas as pd  # to convert input to dataframe
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка модели и данных для предварительной обработки
model_path = "data/rf_class.joblib"
data_path = "data/X_data.csv"

if not os.path.exists(model_path):
    logger.error(f"Файл модели {model_path} не найден.")
    raise FileNotFoundError(f"Файл модели {model_path} не найден.")

if not os.path.exists(data_path):
    logger.error(f"Файл данных {data_path} не найден.")
    raise FileNotFoundError(f"Файл данных {data_path} не найден.")

model = joblib.load(model_path)
logger.info("Модель успешно загружена.")

X = pd.read_csv(data_path, index_col=0)
logger.info("Данные успешно загружены.")

numerical_features = [
    'Age',
    'Number of sexual partners',
    'First sexual intercourse',
    'Num of pregnancies',
    'Smokes (years)',
    'Smokes (packs/year)',
    'Hormonal Contraceptives (years)',
    'IUD (years)',
    'STDs (number)',
]

imputer = KNNImputer(n_neighbors=5)
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
logger.info("Данные успешно пропущены с помощью KNNImputer.")

scaler = StandardScaler()
X_imputed[numerical_features] = scaler.fit_transform(X_imputed[numerical_features])
logger.info("Данные успешно масштабированы с помощью StandardScaler.")

def predict_risk(input_data):
    """
    Функция для предсказания риска заболевания раком шейки матки.
    Принимает словарь с данными, и возвращает вероятность риска.
    """
    try:
        input_df = pd.DataFrame([input_data])
        # Добавляем недостающие столбцы, если они отсутствуют
        for feature in X.columns:
            if feature not in input_df.columns:
                input_df[feature] = np.nan
        logger.info(f"Обрабатываемые данные: {input_df}")

        # Применяем компьютер и масштабирование
        input_df_imputed = pd.DataFrame(imputer.transform(input_df), columns=input_df.columns)
        input_df_imputed[numerical_features] = scaler.transform(input_df_imputed[numerical_features])
        logger.info(f"Обработанные данные для модели: {input_df_imputed}")

        # Предсказание вероятности
        risk_proba = model.predict_proba(input_df_imputed)[0][1]
        logger.info(f"Предсказанная вероятность риска: {risk_proba}")

        return {'Risk Probability': risk_proba}
    except Exception as e:
        logger.exception("Ошибка при предсказании риска.")
        raise
