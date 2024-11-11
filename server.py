# server.py
# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from for_azat import predict_risk
import CV_Azat  # Импортируем модуль с моделью
import openai
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Настройки для загрузки файлов
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Убедимся, что папка для загрузок существует
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Настройка OpenAI API ключа через переменные окружения
OPENAI_API_KEY = 'sk--K2Du6bZkJX4bzg8vTZ14uc30jLe_iNz5MGYpu5l5hT3BlbkFJlN5t0Vr2Sgec9hb8OjKH9CoxSR577qnFV1A4CuKP8A'
# Initialize OpenAI client
client = openai.Client(api_key=OPENAI_API_KEY)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/cytology-analysis')
def cytology_analysis():
    return render_template('cytology_analysis.html')

@app.route('/save-data', methods=['POST'])
def save_data():
    try:
        data = request.get_json()
        if not data:
            logger.error("Данные не предоставлены")
            return jsonify({'error': 'Данные не предоставлены'}), 400

        # Преобразование и обработка данных для модели
        user_input = {
            'Age': int(data.get('age', 0)),
            'Number of sexual partners': int(data.get('numPartners', 0)),
            'First sexual intercourse': int(data.get('firstSex', 0)),
            'Num of pregnancies': int(data.get('numPregnancies', 0)),
            'Smokes': int(data.get('smokes', 0)),
            'Smokes (years)': int(data.get('smokesYears', 0)),
            'Smokes (packs/year)': float(data.get('smokesCigarettesDay', 0)) * 365 / 20,  # Пример преобразования
            'STDs': int(data.get('stds', 0)),
            'STDs (number)': int(data.get('stdsNumber', 0)),
            'Hormonal Contraceptives': int(data.get('hormonalContraceptives', 0)),
            'Hormonal Contraceptives (years)': int(data.get('hormonalContraceptivesYears', 0)),
            'IUD': int(data.get('iud', 0)),
            'IUD (years)': int(data.get('iudYears', 0)),
        }

        logger.info(f"Полученные данные: {user_input}")

        # Получение предсказания от модели
        prediction = predict_risk(user_input)
        risk_percentage = prediction['Risk Probability'] * 100  # Перевод в проценты
        logger.info(f"Предсказание риска: {risk_percentage:.2f}%")

        prompt = f"""Представь, что ты гинеколог, к тебе обращается пациент со следующими результатами опроса:
Возраст: {user_input['Age']}
Количество сексуальных партнёров за всю жизнь: {user_input['Number of sexual partners']}
Первый сексуальный опыт: {user_input['First sexual intercourse']}
Количество беременностей: {user_input['Num of pregnancies']}
Курит ли? (если 1 - да, 0 - нет): {user_input['Smokes']}
Сколько лет курит: {user_input['Smokes (years)']}
Сколько пачек в год курит: {user_input['Smokes (packs/year)']}
Были ли ЗППП? (если 1 - да, 0 - нет): {user_input['STDs']}
Сколько было ЗППП: {user_input['STDs (number)']}
Использует ли гормональные контрацептивы? (если 1 - да, 0 - нет): {user_input['Hormonal Contraceptives']}
Сколько лет использует гормональные контрацептивы: {user_input['Hormonal Contraceptives (years)']}
Использует ли внутриматочные спирали? (если 1 - да, 0 - нет): {user_input['IUD']}
Сколько лет использует внутриматочные спирали: {user_input['IUD (years)']} 

Известно, что вероятность развития рака шейки матки = {risk_percentage:.2f}%

Выведи пациенту комментарий по данной вероятности (низкий или высокий, высокая есть больше 5%), но не выводи самого процента, он уже известен пациенту. Также выведи меры профилактики на основе ответов пациента. Используй обращение к пациенту на "Вы", "у вас" и т.д., не говори от первого лица, пиши нейтрально и коротко. Ответ должен быть коротким и ЦЕЛЬНЫМ ТЕКСТОМ без структуризации, один абзац текста. Постарайся побудить в пациенте желание посетить профессиональный осмотр у специалиста."""

        logger.info("Отправка запроса к OpenAI API.")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {'role': 'system', 'content': prompt}
            ],
            temperature=1,
            max_tokens=2048,
            top_p=1
        )
        recommendation = response.choices[0].message.content.strip()
        logger.info(f"Рекомендация от OpenAI: {recommendation}")

        # Возвращаем результат
        return jsonify({
            'riskPercentage': f"{risk_percentage:.2f}%",
            'recommendation': recommendation
        }), 200

    except Exception as e:
        logger.exception("Ошибка при обработке данных")
        return jsonify({'error': str(e)}), 500

@app.route('/upload-image', methods=['POST'])
def upload_image():
    try:
        if 'cellImage' not in request.files:
            logger.error("Нет загруженного файла")
            return jsonify({'error': 'Нет загруженного файла'}), 400

        file = request.files['cellImage']

        if file.filename == '':
            logger.error("Файл не выбран")
            return jsonify({'error': 'Файл не выбран'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            logger.info(f"Файл сохранён по пути: {filepath}")

            # Вызов вашей ML-модели для анализа изображения
            cancer_type, confidence = CV_Azat.predict_image(
                CV_Azat.model,
                CV_Azat.load_image(filepath, transform=CV_Azat.test_transform),
                CV_Azat.device,
                CV_Azat.reverse_label_map
            )
            confidence = confidence * 100

            cancer_types = {
                'im_Metaplastic': "Метапластический тип",
                'im_Dyskeratotic': "Дискератозный тип",
                'im_Superficial-Intermediate': "Поверхностный промежуточный тип",
                'im_Parabasal': "Парабазальный тип",
                'im_Koilocytotic': "Койлоцитозный тип",
            }

            logger.info(f"Результат анализа: {cancer_types[cancer_type]} с точность {confidence:.2f}%")

            return jsonify({
                'analysisResult': f"Результат анализа: {cancer_types[cancer_type]} с точность {confidence:.2f}%"
            }), 200
        else:
            logger.error("Неверный тип файла")
            return jsonify({'error': 'Неверный тип файла'}), 400
    except Exception as e:
        logger.exception("Ошибка при загрузке изображения")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
