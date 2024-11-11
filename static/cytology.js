// static/cytology.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('cytologyForm');
    const loader = document.getElementById('loader');
    const resultSection = document.getElementById('result');
    const analysisResultEl = document.querySelector('.analysis-result');
    const retakeButton = document.getElementById('retake');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const fileInput = document.getElementById('cellImage');
        const file = fileInput.files[0];

        if (!file) {
            alert('Пожалуйста, выберите файл для загрузки.');
            return;
        }

        loader.classList.remove('hidden'); // Показываем загрузчик

        fetch('/upload-image', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при загрузке файла.');
            }
            return response.json();
        })
        .then(data => {
            loader.classList.add('hidden'); // Скрываем загрузчик

            if (data.error) {
                throw new Error(data.error);
            }

            analysisResultEl.textContent = data.analysisResult;
            resultSection.classList.remove('hidden');
        })
        .catch(error => {
            loader.classList.add('hidden'); // Скрываем загрузчик
            console.error('Error:', error);
            alert(`Произошла ошибка: ${error.message}`);
        });
    });

    retakeButton.addEventListener('click', () => {
        form.reset();
        resultSection.classList.add('hidden');
    });
});
