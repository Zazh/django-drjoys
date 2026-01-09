// ============================================
// MAIN.JS - Общие скрипты для всего сайта
// ============================================

// --------------------------------------------
// 1. МОБИЛЬНОЕ МЕНЮ С УПРАВЛЕНИЕМ ВИДЕО
// --------------------------------------------
function initMobileMenu() {
    const menuBtn = document.getElementById('menuBtn');
    const mainNav = document.getElementById('mainNav');
    const siteHeader = document.querySelector('.site-header');
    const navWrapper = document.querySelector('.nav_wrapper');

    if (!menuBtn || !mainNav || !siteHeader || !navWrapper) return;

    let isMenuActive = false;
    let youtubePlayer = null;

    // Медиа-запрос для десктопа
    const isDesktop = window.matchMedia('(min-width: 1024px)');

    // Инициализация YouTube Player
    function initYouTubePlayer() {
        // Проверяем что API загружен
        if (typeof YT === 'undefined' || typeof YT.Player === 'undefined') {
            console.warn('YouTube API не загружен');
            return;
        }

        youtubePlayer = new YT.Player('navYoutubeVideo', {
            events: {
                'onReady': onPlayerReady
            }
        });
    }

    function onPlayerReady(event) {
        console.log('YouTube player готов');
    }

    // Управление видео
    // Запускаем видео БЕЗ звука (для автозапуска)
    function playVideo() {
        if (youtubePlayer && youtubePlayer.playVideo) {
            youtubePlayer.mute(); // Отключаем звук
            youtubePlayer.playVideo();
        }
    }

    function pauseVideo() {
        if (youtubePlayer && youtubePlayer.pauseVideo) {
            youtubePlayer.pauseVideo();
        }
    }

    // Обработчик клика на кнопку меню
    menuBtn.addEventListener('click', () => {
        isMenuActive = !isMenuActive;

        const lines = menuBtn.querySelectorAll('span');

        if (isMenuActive) {
            // Превращаем кнопку в крестик
            lines[0].style.opacity = '0';
            lines[1].style.transform = 'rotate(45deg)';
            lines[2].style.transform = 'rotate(-45deg)';
            lines[3].style.opacity = '0';

            // Показываем меню
            mainNav.classList.remove('hidden');

            // Добавляем высоту на header ТОЛЬКО на десктопе
            if (isDesktop.matches) {
                siteHeader.classList.add('h-40');
            }

            // Добавляем bottom-0 на nav_wrapper
            navWrapper.classList.add('bottom-0');

            // Меняем backdrop-blur с xs на xl
            navWrapper.classList.remove('backdrop-blur-xs');
            navWrapper.classList.add('backdrop-blur-xl');

            // Запускаем видео
            setTimeout(() => {
                playVideo();
            }, 300); // Небольшая задержка для плавности

        } else {
            // Возвращаем кнопку в гамбургер
            lines[0].style.opacity = '1';
            lines[1].style.transform = 'rotate(0deg)';
            lines[2].style.transform = 'rotate(0deg)';
            lines[3].style.opacity = '1';

            // Скрываем меню
            mainNav.classList.add('hidden');

            // Убираем высоту с header
            siteHeader.classList.remove('h-40');

            // Убираем bottom-0 с nav_wrapper
            navWrapper.classList.remove('bottom-0');

            // Возвращаем backdrop-blur с xl на xs
            navWrapper.classList.remove('backdrop-blur-xl');
            navWrapper.classList.add('backdrop-blur-xs');

            // Останавливаем видео
            pauseVideo();
        }
    });

    // Следим за изменением размера экрана
    isDesktop.addEventListener('change', (e) => {
        if (isMenuActive) {
            if (e.matches) {
                siteHeader.classList.add('h-40');
            } else {
                siteHeader.classList.remove('h-40');
            }
        }
    });

    // Инициализируем YouTube Player после загрузки API
    if (window.YT && window.YT.Player) {
        initYouTubePlayer();
    } else {
        // Ждем загрузки API
        window.onYouTubeIframeAPIReady = function() {
            initYouTubePlayer();
        };
    }
}

window.addEventListener('load', initMobileMenu);

// --------------------------------------------
// 2. ДИНАМИЧЕСКИЙ GAP ДЛЯ СЕТКИ КАРТОЧЕК
// --------------------------------------------
function updateProductGridGap() {
    const referenceCol = document.getElementById('referenceCol');
    const productGrid = document.getElementById('productGrid');

    // Проверяем что элементы существуют
    if (!referenceCol || !productGrid) return;

    // Медиа-запрос для xl брейкпоинта (1280px в Tailwind)
    const isXlOrLarger = window.matchMedia('(min-width: 1280px)');

    // Если экран меньше xl - используем классовые gap
    if (!isXlOrLarger.matches) {
        productGrid.style.gap = '';
        return;
    }

    // Проверяем что эталонная колонка не скрыта
    if (referenceCol.classList.contains('hidden')) {
        // Убираем inline style, чтобы работали классовые gap
        productGrid.style.gap = '';
        return;
    }

    // Получаем ширину эталонной колонки
    const colWidth = referenceCol.offsetWidth;

    // Применяем как gap ТОЛЬКО на xl+
    productGrid.style.gap = `${colWidth}px`;
}

// Вызываем при загрузке
window.addEventListener('load', updateProductGridGap);

// Вызываем при изменении размера окна с debounce
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(updateProductGridGap, 100);
});

// --------------------------------------------
// 3. ПЕРЕКЛЮЧЕНИЕ КАРТИНОК ТОВАРОВ
// --------------------------------------------
function initProductImageSlider() {
    const productCards = document.querySelectorAll('.product-card_picture');

    productCards.forEach(card => {
        const images = card.querySelectorAll('.product-image');
        const imagesCount = images.length;

        if (imagesCount <= 1) return; // Если одна картинка - слайдер не нужен

        // Создаем индикаторы автоматически
        const indicatorsContainer = card.querySelector('.product-indicators');
        indicatorsContainer.innerHTML = ''; // Очищаем на всякий случай

        const indicators = [];
        for (let i = 0; i < imagesCount; i++) {
            const indicator = document.createElement('span');
            indicator.classList.add('indicator');
            indicatorsContainer.appendChild(indicator);
            indicators.push(indicator);
        }

        // Инициализация - показываем первую картинку и индикатор
        images[0].classList.add('active');
        indicators[0].classList.add('active');

        let currentIndex = 0;
        let touchStartX = 0;
        let touchEndX = 0;

        // Функция переключения картинки
        function showImage(index) {
            if (index === currentIndex) return;

            images.forEach(img => img.classList.remove('active'));
            indicators.forEach(ind => ind.classList.remove('active'));

            images[index].classList.add('active');
            indicators[index].classList.add('active');

            currentIndex = index;
        }

        // ==========================================
        // ДЕСКТОП: Движение курсора по зонам
        // ==========================================
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const sectionWidth = rect.width / imagesCount;
            const newIndex = Math.floor(x / sectionWidth);

            if (newIndex >= 0 && newIndex < imagesCount) {
                showImage(newIndex);
            }
        });

        card.addEventListener('mouseleave', () => {
            showImage(0);
        });

        // ==========================================
        // МОБИЛЬНЫЕ: Свайпы влево/вправо
        // ==========================================
        card.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        card.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });

        function handleSwipe() {
            const swipeThreshold = 50;

            if (touchEndX < touchStartX - swipeThreshold) {
                const nextIndex = (currentIndex + 1) % imagesCount;
                showImage(nextIndex);
            }

            if (touchEndX > touchStartX + swipeThreshold) {
                const prevIndex = (currentIndex - 1 + imagesCount) % imagesCount;
                showImage(prevIndex);
            }
        }
    });
}

window.addEventListener('load', initProductImageSlider);

// --------------------------------------------
// 4. АНИМАЦИЯ БИЕНИЯ СЕРДЦА С КУЛЬМИНАЦИЕЙ
// --------------------------------------------
function initHeartbeat() {
    const heartElement = document.querySelector('.heart-beat');
    const dotElement = document.querySelector('.dot-shake');
    const triggers = document.querySelectorAll('.heart-trigger');

    if (!heartElement || triggers.length === 0) return;

    let hoverTimer = null;
    let scaleValue = 1;
    let shakeIntensity = 1;
    let isHovering = false;
    let animationFrame = null;

    // Функция обновления scale и shake intensity
    function updateScale() {
        if (!isHovering) return;

        const elapsed = Date.now() - hoverTimer;
        const totalDuration = 20000; // 20 секунд
        const progress = Math.min(elapsed / totalDuration, 1); // 0 → 1

        // Кривая нарастания:
        if (progress < 0.2) {
            // Прелюдия - БЫСТРЫЙ старт
            const localProgress = progress / 0.2;
            scaleValue = 1 + (localProgress * 0.05);
            shakeIntensity = 1 + (localProgress * 0.5); // 1.0 → 1.5 (быстрее!)
        } else if (progress < 0.5) {
            // Нарастание
            const localProgress = (progress - 0.2) / 0.3;
            scaleValue = 1.05 + (localProgress * 0.05);
            shakeIntensity = 1.5 + (localProgress * 0.5); // 1.5 → 2.0
        } else if (progress < 0.8) {
            // Интенсив
            const localProgress = (progress - 0.5) / 0.3;
            scaleValue = 1.1 + (localProgress * 0.05);
            shakeIntensity = 2.0 + (localProgress * 0.5); // 2.0 → 2.5
        } else {
            // Кульминация - точка растет КАК СЕРДЦЕ
            const localProgress = (progress - 0.8) / 0.2;
            scaleValue = 1.15 + (localProgress * 0.2);
            shakeIntensity = 2.5 + (localProgress * 0.5); // 2.5 → 3.0
        }

        // Если цикл завершен - начинаем заново
        if (elapsed >= totalDuration) {
            hoverTimer = Date.now();
        }

        // Применяем scale для сердца
        heartElement.style.setProperty('--heart-scale', scaleValue);

        // Применяем shake intensity для точки
        if (dotElement) {
            dotElement.style.setProperty('--shake-intensity', shakeIntensity);
        }

        // Продолжаем анимацию
        animationFrame = requestAnimationFrame(updateScale);
    }

    // Обработчики для триггеров
    triggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', () => {
            isHovering = true;
            hoverTimer = Date.now();
            scaleValue = 1;
            shakeIntensity = 1;

            heartElement.classList.add('is-beating');
            if (dotElement) {
                dotElement.classList.add('is-shaking');
            }

            animationFrame = requestAnimationFrame(updateScale);
        });

        trigger.addEventListener('mouseleave', () => {
            isHovering = false;
            heartElement.classList.remove('is-beating');
            heartElement.style.setProperty('--heart-scale', 1);

            if (dotElement) {
                dotElement.classList.remove('is-shaking');
                dotElement.style.setProperty('--shake-intensity', 1);
            }

            if (animationFrame) {
                cancelAnimationFrame(animationFrame);
                animationFrame = null;
            }
        });
    });
}

window.addEventListener('load', initHeartbeat);

// --------------------------------------------
// 5. FAQ АККОРДЕОН
// --------------------------------------------
function initFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');

    if (faqItems.length === 0) return;

    faqItems.forEach((item, index) => {
        const button = item.querySelector('.faq-button');
        const panel = item.querySelector('.faq-panel');

        if (!button || !panel) return;

        // Генерируем уникальные ID автоматически
        const buttonId = `faq-button-${index + 1}`;
        const panelId = `faq-panel-${index + 1}`;

        // Устанавливаем ID и aria-атрибуты
        button.id = buttonId;
        button.setAttribute('aria-expanded', 'false');
        button.setAttribute('aria-controls', panelId);

        panel.id = panelId;
        panel.setAttribute('role', 'region');
        panel.setAttribute('aria-labelledby', buttonId);

        // Обработчик клика
        button.addEventListener('click', () => {
            const isExpanded = button.getAttribute('aria-expanded') === 'true';

            // Закрываем все остальные (опционально - убери если хочешь чтобы несколько было открыто)
            faqItems.forEach((otherItem) => {
                const otherButton = otherItem.querySelector('.faq-button');
                const otherPanel = otherItem.querySelector('.faq-panel');

                if (otherButton !== button) {
                    otherButton.setAttribute('aria-expanded', 'false');
                    otherPanel.classList.remove('is-open');
                }
            });

            // Переключаем текущий элемент
            if (isExpanded) {
                button.setAttribute('aria-expanded', 'false');
                panel.classList.remove('is-open');
            } else {
                button.setAttribute('aria-expanded', 'true');
                panel.classList.add('is-open');
            }
        });
    });
}

window.addEventListener('load', initFAQ);

// --------------------------------------------
// 6. ДОБАВИТЬ В КОРЗИНУ - ВЫПАДАЮЩИЙ СПИСОК
// --------------------------------------------
function initAddToCart() {
    const addToCartBlocks = document.querySelectorAll('.add-to-cart');

    if (addToCartBlocks.length === 0) return;

    addToCartBlocks.forEach(block => {
        const button = block.querySelector('.btn-cat');
        const buttonWrapper = block.querySelector('.cart-button-wrapper');
        const linksWrapper = block.querySelector('.cart-links-wrapper');

        if (!button || !buttonWrapper || !linksWrapper) return;

        // Клик на кнопку - открываем список
        button.addEventListener('click', (e) => {
            e.stopPropagation();

            // Закрываем все другие открытые блоки
            addToCartBlocks.forEach(otherBlock => {
                if (otherBlock !== block) {
                    const otherButtonWrapper = otherBlock.querySelector('.cart-button-wrapper');
                    const otherLinksWrapper = otherBlock.querySelector('.cart-links-wrapper');

                    otherBlock.classList.remove('active');
                    otherButtonWrapper.classList.remove('hidden');
                    otherLinksWrapper.classList.add('hidden');
                }
            });

            // Открываем текущий блок
            block.classList.add('active');
            buttonWrapper.classList.add('hidden');
            linksWrapper.classList.remove('hidden');
        });

        // Клик вне блока - закрываем
        document.addEventListener('click', (e) => {
            if (!block.contains(e.target)) {
                block.classList.remove('active');
                buttonWrapper.classList.remove('hidden');
                linksWrapper.classList.add('hidden');
            }
        });

        // Останавливаем всплытие при клике внутри блока
        block.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    });
}

window.addEventListener('load', initAddToCart);



// --------------------------------------------
// 8. СЛАЙДЕР ПРОДУКТА С АВТОПРОКРУТКОЙ
// --------------------------------------------
function initProductSlider() {
    const sliders = document.querySelectorAll('.product-slider');

    if (sliders.length === 0) return;

    sliders.forEach(slider => {
        const images = slider.querySelectorAll('.slider-image');
        const indicatorsContainer = slider.querySelector('.slider-indicators');
        const playPauseBtn = slider.querySelector('.slider-play-pause');
        const pauseIcon = playPauseBtn?.querySelector('.pause-icon');
        const playIcon = playPauseBtn?.querySelector('.play-icon');
        const progressBar = slider.querySelector('.progress-bar');

        const imagesCount = images.length;

        if (imagesCount <= 1) return;

        // Создаем индикаторы
        indicatorsContainer.innerHTML = '';
        const indicators = [];
        for (let i = 0; i < imagesCount; i++) {
            const indicator = document.createElement('span');
            indicator.classList.add('indicator');
            indicatorsContainer.appendChild(indicator);
            indicators.push(indicator);
        }

        // Параметры
        const autoplay = slider.getAttribute('data-autoplay') === 'true';
        const interval = parseInt(slider.getAttribute('data-interval')) || 5000;

        let currentIndex = 0;
        let autoplayTimer = null;
        let progressTimer = null;
        let isPlaying = autoplay;
        let isHovered = false; // НОВЫЙ ФЛАГ

        // Показать картинку
        function showImage(index) {
            images.forEach(img => img.classList.remove('active'));
            indicators.forEach(ind => ind.classList.remove('active'));

            images[index].classList.add('active');
            indicators[index].classList.add('active');

            currentIndex = index;
        }

        // Следующая картинка
        function nextImage() {
            const nextIndex = (currentIndex + 1) % imagesCount;
            showImage(nextIndex);
        }

        // Обновление прогресс-бара
        function updateProgress() {
            if (!isPlaying || isHovered) return; // ПРОВЕРЯЕМ isHovered

            let progress = 0;
            const step = 100 / (interval / 100);

            progressTimer = setInterval(() => {
                if (isHovered) return; // ПРОВЕРЯЕМ isHovered

                progress += step;
                const offset = 100 - progress;
                progressBar.style.strokeDashoffset = offset;

                if (progress >= 100) {
                    clearInterval(progressTimer);
                }
            }, 100);
        }

        // Старт автопрокрутки
        function startAutoplay() {
            if (!isPlaying || isHovered) return; // ПРОВЕРЯЕМ isHovered

            stopAutoplay();

            // Сброс прогресса
            progressBar.style.strokeDashoffset = 100;

            // Запуск прогресс-бара
            updateProgress();

            // Запуск автопрокрутки
            autoplayTimer = setTimeout(() => {
                if (isHovered) return; // ПРОВЕРЯЕМ перед переключением
                nextImage();
                startAutoplay();
            }, interval);
        }

        // Остановка автопрокрутки
        function stopAutoplay() {
            if (autoplayTimer) {
                clearTimeout(autoplayTimer);
                autoplayTimer = null;
            }
            if (progressTimer) {
                clearInterval(progressTimer);
                progressTimer = null;
            }
        }

        // Toggle play/pause
        function togglePlayPause() {
            isPlaying = !isPlaying;

            if (isPlaying) {
                pauseIcon.classList.remove('hidden');
                playIcon.classList.add('hidden');
                playPauseBtn.setAttribute('aria-label', 'Pause slideshow');
                if (!isHovered) { // Запускаем только если не наведен курсор
                    startAutoplay();
                }
            } else {
                pauseIcon.classList.add('hidden');
                playIcon.classList.remove('hidden');
                playPauseBtn.setAttribute('aria-label', 'Play slideshow');
                stopAutoplay();
                progressBar.style.strokeDashoffset = 100;
            }
        }

        // Инициализация
        showImage(0);
        if (autoplay) {
            startAutoplay();
        }

        // События

        // Клик на кнопку play/pause
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                togglePlayPause();
            });
        }

        // ДЕСКТОП: Наведение мыши - полная остановка
        slider.addEventListener('mouseenter', () => {
            isHovered = true;
            stopAutoplay(); // ПОЛНОСТЬЮ ОСТАНАВЛИВАЕМ
        });

        slider.addEventListener('mouseleave', () => {
            isHovered = false;
            if (isPlaying) {
                startAutoplay(); // ПЕРЕЗАПУСКАЕМ
            }
        });

        // МОБИЛЬНЫЙ: Клик на картинку - toggle play/pause
        slider.addEventListener('click', (e) => {
            if (e.target.closest('.slider-play-pause')) return;

            if (window.innerWidth < 1024) {
                togglePlayPause();
            }
        });

        // Свайпы для мобильных
        let touchStartX = 0;
        let touchEndX = 0;

        slider.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        slider.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });

        function handleSwipe() {
            const swipeThreshold = 50;

            if (touchEndX < touchStartX - swipeThreshold) {
                const nextIndex = (currentIndex + 1) % imagesCount;
                showImage(nextIndex);
                if (isPlaying) {
                    startAutoplay();
                }
            }

            if (touchEndX > touchStartX + swipeThreshold) {
                const prevIndex = (currentIndex - 1 + imagesCount) % imagesCount;
                showImage(prevIndex);
                if (isPlaying) {
                    startAutoplay();
                }
            }
        }
    });
}

window.addEventListener('load', initProductSlider);


// --------------------------------------------
// 9. DRAG КАРУСЕЛЬ С КАСТОМНЫМ КУРСОРОМ
// --------------------------------------------
function initDragCarousel() {
    const carouselWrappers = document.querySelectorAll('.carousel-wrapper');

    if (carouselWrappers.length === 0) return;

    carouselWrappers.forEach(wrapper => {
        const cursor = wrapper.querySelector('.carousel-cursor');

        if (!cursor) return;

        let isDragging = false;
        let startX = 0;
        let scrollLeft = 0;
        let hasMoved = false; // Флаг для отслеживания движения

        // Обновление позиции кастомного курсора
        function updateCursorPosition(e) {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        }

        // Начало драга
        function startDrag(e) {
            // Запускаем драг на любом элементе внутри wrapper
            isDragging = true;
            hasMoved = false;
            wrapper.classList.add('is-dragging');

            startX = e.pageX - wrapper.offsetLeft;
            scrollLeft = wrapper.scrollLeft;

            wrapper.style.scrollBehavior = 'auto';

            // Запрещаем выделение текста
            e.preventDefault();
        }

        // Процесс драга
        function drag(e) {
            if (!isDragging) return;

            e.preventDefault();
            hasMoved = true; // Зафиксировали что было движение

            const x = e.pageX - wrapper.offsetLeft;
            const walk = (x - startX) * 1.5;
            wrapper.scrollLeft = scrollLeft - walk;
        }

        // Конец драга
        function endDrag(e) {
            if (!isDragging) return;

            isDragging = false;

            // Блокируем клики если было движение
            if (hasMoved) {
                setTimeout(() => {
                    wrapper.classList.remove('is-dragging');
                }, 10);
            } else {
                wrapper.classList.remove('is-dragging');
            }

            wrapper.style.scrollBehavior = 'smooth';
        }

        // Движение мыши
        wrapper.addEventListener('mousemove', (e) => {
            updateCursorPosition(e);

            if (isDragging) {
                drag(e);
            }
        });

        // События драга - на самом wrapper
        wrapper.addEventListener('mousedown', startDrag);
        wrapper.addEventListener('mouseup', endDrag);
        wrapper.addEventListener('mouseleave', endDrag);

        // Дополнительная защита - блокируем клики при драге
        wrapper.addEventListener('click', (e) => {
            if (hasMoved) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                hasMoved = false;
            }
        }, true);
    });
}

window.addEventListener('load', initDragCarousel);