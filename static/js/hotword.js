document.addEventListener('DOMContentLoaded', function () {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://127.0.0.1:8000/api/v1/hotword', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            const jsonData = response.data; 
            const jsonDataElement = document.querySelector('.tm-mb-41');
            // const jsonDataText = JSON.stringify(jsonData, null, 2);
            // jsonDataElement.innerHTML = jsonDataText; 
            const jsonDataItems = jsonData.map(item => `<p>${item.keyword}</p>`);
            jsonDataElement.innerHTML = jsonDataItems.join('');
        } else {
            console.error('error', xhr.status);
        }
        }
    };
    xhr.send();
});