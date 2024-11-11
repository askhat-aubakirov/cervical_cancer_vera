// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('riskForm');
    const resultSection = document.getElementById('result');
    const riskPercentageEl = document.querySelector('.risk-percentage');
    const retakeButton = document.getElementById('retake');
    const loader = document.getElementById('loader'); // Добавлено для загрузчика

    // Функция для управления отображением и атрибутами полей
    const toggleField = (radioName, valueToShow, fieldIds) => {
        const radios = document.getElementsByName(radioName);
        fieldIds.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            const fieldGroup = field.parentElement;

            // Изначально скрываем поле
            fieldGroup.style.display = 'none';
            field.removeAttribute('required');

            radios.forEach(radio => {
                radio.addEventListener('change', function () {
                    if (this.value === valueToShow) {
                        fieldGroup.style.display = 'block';
                        field.setAttribute('required', 'required');
                        field.value = ''; // Очистка значения при выборе "Да"
                    } else {
                        fieldGroup.style.display = 'none';
                        field.removeAttribute('required');
                        field.value = '0'; // Устанавливаем значение '0' при выборе "Нет"
                    }
                });
            });
        });
    };

    // Управление полями на основе ответов пользователя
    toggleField('smokes', '1', ['smokesYears', 'smokesCigarettesDay']);
    toggleField('stds', '1', ['stdsNumber']);
    toggleField('hormonalContraceptives', '1', ['hormonalContraceptivesYears']);
    toggleField('iud', '1', ['iudYears']);

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Сбор данных формы
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Показываем загрузчик
        loader.classList.remove('hidden');

        // Отправка данных на сервер
        fetch('/save-data', { // Используем относительный путь
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data) // Отправляем JSON
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }
            return response.json();
        })
        .then(responseData => {
            // Скрываем загрузчик
            loader.classList.add('hidden');

            if (responseData.error) {
                throw new Error(`Server error: ${responseData.error}`);
            }
            // Отображение результата
            riskPercentageEl.textContent = responseData.riskPercentage;
            const recommendationEl = document.querySelector('.risk-description');
            recommendationEl.textContent = responseData.recommendation;
            form.classList.add('hidden');
            resultSection.classList.remove('hidden');
        })
        .catch((error) => {
            // Скрываем загрузчик
            loader.classList.add('hidden');

            console.error('Error:', error);
            alert('Произошла ошибка при отправке данных. Пожалуйста, попробуйте позже.');
        });
    });

    retakeButton.addEventListener('click', () => {
        form.reset();
        form.classList.remove('hidden');
        resultSection.classList.add('hidden');

        // Скрыть дополнительные поля после сброса формы и установить '0'
        ['smokesYears', 'smokesCigarettesDay', 'stdsNumber', 'hormonalContraceptivesYears', 'iudYears'].forEach(fieldId => {
            const field = document.getElementById(fieldId);
            const fieldGroup = field.parentElement;
            fieldGroup.style.display = 'none';
            field.removeAttribute('required');
            field.value = '0';
        });
    });
});
