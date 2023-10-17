const slider = document.querySelector('.slider');

fetch('/api/v1/hot_drink')
    .then(response => response.json())
    .then(data => {
        data.data.forEach(item => {
            const sliderItem = document.createElement('div');
            sliderItem.classList.add('slider-item');
            
            const img = document.createElement('img');
            img.src = item.img;
            sliderItem.appendChild(img);
            
            const store = document.createElement('div');
            store.classList.add('drink-store');
            store.textContent = item.store;
            sliderItem.appendChild(store);
            
            const name = document.createElement('div');
            name.classList.add('drink-name');
            name.textContent = item.drink_name;
            sliderItem.appendChild(name);
            
            slider.appendChild(sliderItem);
        });

        $('.slider').slick({
            autoplay: true,
            autoplaySpeed: 3000,
            infinite: true,
            slidesToShow: 3,
            slidesToScroll: 1
        });
    })
    .catch(error => {
        console.error('發生錯誤:', error);
    });
