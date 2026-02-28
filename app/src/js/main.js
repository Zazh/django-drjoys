// ============================================
// MAIN.JS - Общие скрипты для всего сайта
// ============================================

// --------------------------------------------
// 0. УНИВЕРСАЛЬНЫЕ УТИЛИТЫ МОДАЛОК
// --------------------------------------------
function openModal(overlay) {
    if (!overlay) return;
    overlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal(overlay) {
    if (!overlay) return;
    overlay.classList.add('hidden');
    document.body.style.overflow = '';
    // Reset to step 1
    const steps = overlay.querySelectorAll('.modal-step');
    steps.forEach((step, i) => {
        step.classList.toggle('hidden', i !== 0);
    });
}

function goToStep(overlay, stepNum) {
    if (!overlay) return;
    overlay.querySelectorAll('.modal-step').forEach(step => {
        step.classList.toggle('hidden', step.dataset.step !== String(stepNum));
    });
}

// Phone mask — автоопределение длины кода страны
function initPhoneMasks() {
    document.querySelectorAll('input[type="tel"]').forEach(phoneInput => {
        if (phoneInput.dataset.maskInit) return;
        phoneInput.dataset.maskInit = '1';

        function formatPhone(digits) {
            if (!digits.length) return '';

            let codeLen = 1;
            if (digits.startsWith('7') || digits.startsWith('1')) codeLen = 1;
            else if (digits.startsWith('99')) codeLen = 3;
            else codeLen = 2;

            const code = digits.slice(0, codeLen);
            const rest = digits.slice(codeLen);

            let formatted = '+' + code;
            if (rest.length > 0) formatted += ' (' + rest.slice(0, 3);
            if (rest.length >= 3) formatted += ')';
            if (rest.length > 3) formatted += ' ' + rest.slice(3, 6);
            if (rest.length > 6) formatted += '-' + rest.slice(6, 8);
            if (rest.length > 8) formatted += '-' + rest.slice(8, 10);

            return formatted;
        }

        phoneInput.addEventListener('input', (e) => {
            let digits = e.target.value.replace(/\D/g, '');
            if (digits.length > 15) digits = digits.slice(0, 15);
            e.target.value = formatPhone(digits);
        });

        phoneInput.addEventListener('focus', () => {
            if (!phoneInput.value) phoneInput.value = '+';
        });

        phoneInput.addEventListener('blur', () => {
            if (phoneInput.value === '+') phoneInput.value = '';
        });

        phoneInput.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && phoneInput.value.length <= 1) {
                phoneInput.value = '';
                e.preventDefault();
            }
        });
    });
}

// Escape key — закрывает все видимые модалки
document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.modal-overlay:not(.hidden)').forEach(overlay => {
        closeModal(overlay);
    });
});

// Click on overlay background — закрывает модалку
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        closeModal(e.target);
    }
});

// Click on .modal-close — закрывает ближайшую модалку
document.addEventListener('click', (e) => {
    const closeBtn = e.target.closest('.modal-close');
    if (!closeBtn) return;
    const overlay = closeBtn.closest('.modal-overlay');
    if (overlay) closeModal(overlay);
});

// Инициализация масок телефона при загрузке
window.addEventListener('load', initPhoneMasks);

// --------------------------------------------
// 1. БУРГЕР-МЕНЮ
// --------------------------------------------
function initMobileMenu() {
    const menuBtn = document.getElementById('menuBtn');
    const mainNav = document.getElementById('mainNav');
    const navWrapper = document.querySelector('.nav_wrapper');

    if (!menuBtn || !mainNav || !navWrapper) return;

    let isMenuActive = false;

    menuBtn.addEventListener('click', () => {
        isMenuActive = !isMenuActive;
        const lines = menuBtn.querySelectorAll('span');

        if (isMenuActive) {
            // Бургер → крестик
            lines[0].style.opacity = '0';
            lines[1].style.transform = 'rotate(45deg)';
            lines[2].style.transform = 'rotate(-45deg)';
            lines[3].style.opacity = '0';

            // Показываем меню
            mainNav.classList.remove('hidden');
            mainNav.classList.add('flex');
            navWrapper.classList.add('bottom-0');
            navWrapper.classList.remove('backdrop-blur-xs');
            navWrapper.classList.add('backdrop-blur-xl');
        } else {
            // Крестик → бургер
            lines[0].style.opacity = '1';
            lines[1].style.transform = 'rotate(0deg)';
            lines[2].style.transform = 'rotate(0deg)';
            lines[3].style.opacity = '1';

            // Скрываем меню
            mainNav.classList.add('hidden');
            mainNav.classList.remove('flex');
            navWrapper.classList.remove('bottom-0');
            navWrapper.classList.remove('backdrop-blur-xl');
            navWrapper.classList.add('backdrop-blur-xs');
        }
    });
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

// ============================================
// SHOP — МОДАЛКИ МАГАЗИНА
// ============================================

// --------------------------------------------
// 10. FLOATING NAV — открытие модалок
// --------------------------------------------
function initFloatingNav() {
    document.querySelectorAll('[data-open-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.dataset.openModal;
            const modal = document.getElementById(modalId);
            if (modal) openModal(modal);
        });
    });
}

window.addEventListener('load', initFloatingNav);

// --------------------------------------------
// 11. PRODUCT BUY — размеры + модалка заказа
// --------------------------------------------
function initProductBuy() {
    const sym = window.DRJOYS?.currencySymbol || '₸';
    let sizeSelected = false;

    // --- Size dropdown (Lamoda-style) ---
    const dropdown = document.getElementById('sizeDropdown');
    const triggerBtn = document.getElementById('sizeDropdownBtn');
    const menu = document.getElementById('sizeMenu');
    const selectedName = document.getElementById('selectedSizeName');

    function openDropdown() {
        if (!menu || !dropdown) return;
        menu.classList.remove('hidden');
        dropdown.classList.add('open');
    }

    function closeDropdown() {
        if (!menu || !dropdown) return;
        menu.classList.add('hidden');
        dropdown.classList.remove('open');
    }

    function selectSize(item) {
        sizeSelected = true;

        // Update active state
        menu.querySelectorAll('.size-dropdown__item--active').forEach(el => el.classList.remove('size-dropdown__item--active'));
        item.classList.add('size-dropdown__item--active');

        // Update trigger: remove placeholder style, show size name
        triggerBtn.classList.remove('size-dropdown__trigger--placeholder');
        if (selectedName) selectedName.textContent = item.dataset.size;

        // Show & update SKU
        const skuBlock = document.getElementById('skuBlock');
        const skuEl = document.getElementById('productSku');
        if (skuBlock) skuBlock.classList.remove('hidden');
        if (skuEl) skuEl.textContent = item.dataset.sku;

        // Show & update price
        const priceRow = document.getElementById('priceRow');
        const priceCurrentEl = document.getElementById('priceCurrent');
        const priceOldEl = document.getElementById('priceOld');
        const priceDiscountEl = document.getElementById('priceDiscount');

        if (priceRow) priceRow.classList.remove('hidden');
        if (priceCurrentEl) priceCurrentEl.textContent = item.dataset.price + ' ' + sym;

        if (priceOldEl && priceDiscountEl) {
            if (item.dataset.oldPrice) {
                priceOldEl.textContent = item.dataset.oldPrice + ' ' + sym;
                priceDiscountEl.textContent = '-' + item.dataset.discount + '%';
                priceOldEl.classList.remove('hidden');
                priceDiscountEl.classList.remove('hidden');
            } else {
                priceOldEl.classList.add('hidden');
                priceDiscountEl.classList.add('hidden');
            }
        }

        closeDropdown();
    }

    if (dropdown && triggerBtn && menu) {
        // Toggle dropdown
        triggerBtn.addEventListener('click', () => {
            const isOpen = !menu.classList.contains('hidden');
            if (isOpen) closeDropdown();
            else openDropdown();
        });

        // Close on click outside (ignore buy button — it opens dropdown itself)
        document.addEventListener('click', (e) => {
            const buyBtn = document.getElementById('buyAnonymousBtn');
            if (!dropdown.contains(e.target) && e.target !== buyBtn) closeDropdown();
        });

        // Select size on click
        menu.querySelectorAll('.size-dropdown__item:not(.size-dropdown__item--disabled)').forEach(item => {
            item.addEventListener('click', () => selectSize(item));
        });
    }

    // --- Buy button: if no size → open dropdown, else → add to cart ---
    const buyBtn = document.getElementById('buyAnonymousBtn');
    let inCart = false;

    function setBuyBtnState(added) {
        if (!buyBtn) return;
        inCart = added;
        if (added) {
            buyBtn.textContent = (window.DRJOYS?.i18n?.addMore || 'Добавить ещё');
            buyBtn.classList.add('btn-cat--active');
        }
    }

    if (buyBtn) {
        buyBtn.addEventListener('click', () => {
            if (!sizeSelected) {
                openDropdown();
                return;
            }

            if (!inCart) {
                // First add — open cart
                setBuyBtnState(true);
                const cartModal = document.getElementById('modalCart');
                if (cartModal) openModal(cartModal);
            } else {
                // Already in cart — +1 qty to first cart item with matching size
                const selectedSize = menu.querySelector('.size-dropdown__item--active');
                const sizeName = selectedSize ? selectedSize.dataset.size : '';
                const cartItems = document.querySelectorAll('#cartItemsList .cart-item');
                let found = false;
                cartItems.forEach(item => {
                    if (found) return;
                    const sizeEl = item.querySelector('.text-\\[10px\\].text-gray-500');
                    if (sizeEl && sizeEl.textContent.includes(sizeName)) {
                        const qtyEl = item.querySelector('.cart-item-qty');
                        if (qtyEl) {
                            const qty = parseInt(qtyEl.textContent) || 1;
                            if (qty < 99) qtyEl.textContent = qty + 1;
                            found = true;
                        }
                    }
                });
                // Flash feedback on button
                buyBtn.textContent = (window.DRJOYS?.i18n?.added || 'Добавлено!');
                setTimeout(() => { buyBtn.textContent = (window.DRJOYS?.i18n?.addMore || 'Добавить ещё'); }, 800);
            }
        });
    }

    // --- Favorite button toggle ---
    const favBtn = document.getElementById('productFavoriteBtn');
    if (favBtn) {
        const favPath = favBtn.querySelector('svg path');
        favBtn.addEventListener('click', () => {
            const isActive = favBtn.classList.toggle('active');
            if (favPath) {
                favPath.setAttribute('fill', isActive ? 'currentColor' : 'none');
            }
        });
    }
}

window.addEventListener('load', initProductBuy);

// --------------------------------------------
// 12. ORDER QUANTITY — счётчик + цена
// --------------------------------------------
function initOrderQuantity() {
    const qtyMinus = document.getElementById('qtyMinus');
    const qtyPlus = document.getElementById('qtyPlus');
    const qtyValue = document.getElementById('qtyValue');

    if (!qtyMinus || !qtyPlus || !qtyValue) return;

    const unitPrice = 690;

    qtyMinus.addEventListener('click', () => {
        let val = parseInt(qtyValue.textContent) || 1;
        if (val > 1) {
            qtyValue.textContent = val - 1;
            updateOrderTotal();
        }
    });

    qtyPlus.addEventListener('click', () => {
        let val = parseInt(qtyValue.textContent) || 1;
        if (val < 99) {
            qtyValue.textContent = val + 1;
            updateOrderTotal();
        }
    });

    // Add to cart button
    const addToCartBtn = document.getElementById('addToCartBtn');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', () => {
            closeModal(document.getElementById('modalOrderQuantity'));
        });
    }

    // Go to delivery
    const goToDeliveryBtn = document.getElementById('goToDeliveryBtn');
    if (goToDeliveryBtn) {
        goToDeliveryBtn.addEventListener('click', () => {
            closeModal(document.getElementById('modalOrderQuantity'));
            const deliveryModal = document.getElementById('modalDelivery');
            if (deliveryModal) {
                setTimeout(() => openModal(deliveryModal), 200);
            }
        });
    }
}

function updateOrderTotal() {
    const qtyValue = document.getElementById('qtyValue');
    const totalEl = document.getElementById('orderTotalPrice');
    if (!qtyValue || !totalEl) return;

    const unitPrice = 690;
    const qty = parseInt(qtyValue.textContent) || 1;
    const total = unitPrice * qty;
    const sym = window.DRJOYS?.currencySymbol || '₸';
    totalEl.textContent = total.toLocaleString('ru-RU') + ' ' + sym;
}

window.addEventListener('load', initOrderQuantity);

// --------------------------------------------
// 13. CART MODAL — количество, удаление
// --------------------------------------------
function initCartModal() {
    const cartOverlay = document.getElementById('modalCart');
    if (!cartOverlay) return;

    function updateCartEmpty() {
        const items = cartOverlay.querySelectorAll('.cart-item');
        const emptyEl = document.getElementById('cartEmpty');
        const listEl = document.getElementById('cartItemsList');
        const footerEl = document.getElementById('cartFooter');
        const isEmpty = items.length === 0;
        if (emptyEl) { emptyEl.classList.toggle('hidden', !isEmpty); emptyEl.classList.toggle('flex', isEmpty); }
        if (listEl) listEl.classList.toggle('hidden', isEmpty);
        if (footerEl) footerEl.classList.toggle('hidden', isEmpty);
    }

    function updateCartTotals() {
        const sym = window.DRJOYS?.currencySymbol || '₸';
        const items = cartOverlay.querySelectorAll('.cart-item');
        let total = 0;
        let oldTotal = 0;

        updateCartEmpty();

        items.forEach(item => {
            const qty = parseInt(item.querySelector('.cart-item-qty').textContent) || 1;
            const price = parseFloat(item.dataset.price) || 0;
            const oldPrice = parseFloat(item.dataset.oldPrice) || 0;
            const itemTotal = price * qty;
            const itemOldTotal = oldPrice ? oldPrice * qty : 0;
            total += itemTotal;
            oldTotal += itemOldTotal || itemTotal;

            // Update per-item prices
            const itemPriceEl = item.querySelector('.cart-item-price');
            const itemOldPriceEl = item.querySelector('.cart-item-old-price');
            if (itemPriceEl) itemPriceEl.textContent = itemTotal.toLocaleString('ru-RU') + ' ' + sym;
            if (itemOldPriceEl) {
                if (oldPrice && oldPrice > price) {
                    itemOldPriceEl.textContent = itemOldTotal.toLocaleString('ru-RU') + ' ' + sym;
                    itemOldPriceEl.classList.remove('hidden');
                } else {
                    itemOldPriceEl.classList.add('hidden');
                }
            }
        });

        const cartTotalEl = document.getElementById('cartTotal');
        const cartOldTotalEl = document.getElementById('cartOldTotal');
        const cartSavingsEl = document.getElementById('cartSavings');

        if (cartTotalEl) cartTotalEl.textContent = total.toLocaleString('ru-RU') + ' ' + sym;

        const savings = oldTotal - total;
        if (savings > 0 && cartOldTotalEl && cartSavingsEl) {
            cartOldTotalEl.textContent = oldTotal.toLocaleString('ru-RU') + ' ' + sym;
            cartOldTotalEl.classList.remove('hidden');
            const percent = Math.round((savings / oldTotal) * 100);
            cartSavingsEl.textContent = '-' + percent + '%';
            cartSavingsEl.classList.remove('hidden');
        } else {
            if (cartOldTotalEl) cartOldTotalEl.classList.add('hidden');
            if (cartSavingsEl) cartSavingsEl.classList.add('hidden');
        }
    }

    function updateMinusBtn(item) {
        const qty = parseInt(item.querySelector('.cart-item-qty').textContent) || 1;
        const minusBtn = item.querySelector('.cart-qty-btn[data-action="minus"], .cart-qty-btn[data-action="remove"]');
        if (!minusBtn) return;
        if (qty <= 1) {
            minusBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>';
            minusBtn.dataset.action = 'remove';
        } else {
            minusBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M3 8H13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
            minusBtn.dataset.action = 'minus';
        }
    }

    // Quantity & remove buttons
    cartOverlay.addEventListener('click', (e) => {
        const btn = e.target.closest('.cart-qty-btn');
        if (!btn) return;

        const item = btn.closest('.cart-item');
        const qtyEl = item.querySelector('.cart-item-qty');
        let qty = parseInt(qtyEl.textContent) || 1;

        if (btn.dataset.action === 'remove') {
            item.remove();
            updateCartTotals();
            return;
        }
        if (btn.dataset.action === 'minus' && qty > 1) {
            qtyEl.textContent = qty - 1;
        } else if (btn.dataset.action === 'plus' && qty < 99) {
            qtyEl.textContent = qty + 1;
        }
        updateMinusBtn(item);
        updateCartTotals();
    });

    // Init on load
    cartOverlay.querySelectorAll('.cart-item').forEach(updateMinusBtn);
    updateCartTotals();

    // Checkout button → open delivery modal
    const checkoutBtn = document.getElementById('cartCheckoutBtn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            closeModal(cartOverlay);
            const deliveryModal = document.getElementById('modalDelivery');
            if (deliveryModal) {
                setTimeout(() => openModal(deliveryModal), 200);
            }
        });
    }

    // Continue shopping button
    const continueBtn = document.getElementById('cartContinueBtn');
    if (continueBtn) {
        continueBtn.addEventListener('click', () => closeModal(cartOverlay));
    }
}

window.addEventListener('load', initCartModal);

// --------------------------------------------
// 14. FAVORITES MODAL — удаление
// --------------------------------------------
function initFavoritesModal() {
    const favOverlay = document.getElementById('modalFavorites');
    if (!favOverlay) return;

    // Remove button
    favOverlay.addEventListener('click', (e) => {
        const btn = e.target.closest('.fav-remove-btn');
        if (!btn) return;

        const item = btn.closest('.fav-item');
        if (item) {
            item.remove();
            // Check if list is empty
            const list = document.getElementById('favoritesList');
            const empty = document.getElementById('favoritesEmpty');
            if (list && list.children.length === 0 && empty) {
                empty.classList.remove('hidden');
                empty.classList.add('flex');
            }
        }
    });

    // Close on overlay click
    favOverlay.addEventListener('click', (e) => {
        if (e.target === favOverlay) closeModal(favOverlay);
    });
}

window.addEventListener('load', initFavoritesModal);

// --------------------------------------------
// 15. PROFILE MODAL — навигация по шагам
// --------------------------------------------
function initProfileModal() {
    const profileOverlay = document.getElementById('modalProfile');
    if (!profileOverlay) return;

    const backBtn = document.getElementById('profileBackBtn');
    let stepHistory = ['1'];

    function resetProfile() {
        stepHistory = ['1'];
        if (backBtn) backBtn.classList.add('hidden');
        closeModal(profileOverlay);
    }

    function goToProfileStep(stepNum) {
        // Prevent duplicate pushes
        if (stepHistory[stepHistory.length - 1] !== stepNum) {
            stepHistory.push(stepNum);
        }
        goToStep(profileOverlay, stepNum);

        if (backBtn) {
            backBtn.classList.toggle('hidden', stepHistory.length <= 1);
        }
    }

    // Menu buttons
    profileOverlay.querySelectorAll('[data-profile-step]').forEach(btn => {
        btn.addEventListener('click', () => {
            goToProfileStep(btn.dataset.profileStep);
        });
    });

    // Back button
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            stepHistory.pop();
            const prevStep = stepHistory[stepHistory.length - 1] || '1';
            goToStep(profileOverlay, prevStep);
            backBtn.classList.toggle('hidden', stepHistory.length <= 1);
        });
    }

    // Close button (remove inline onclick, use JS)
    const closeBtn = profileOverlay.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.removeAttribute('onclick');
        closeBtn.addEventListener('click', resetProfile);
    }

    // Logout
    const logoutBtn = document.getElementById('profileLogoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', resetProfile);
    }

    // Close on overlay click
    profileOverlay.addEventListener('click', (e) => {
        if (e.target === profileOverlay) resetProfile();
    });
}

window.addEventListener('load', initProfileModal);

// --------------------------------------------
// 16. AUTH MODAL — Telegram / Email
// --------------------------------------------
function initAuthModal() {
    const authOverlay = document.getElementById('modalAuth');
    if (!authOverlay) return;

    const backBtn = document.getElementById('authBackBtn');

    function resetAuth() {
        if (backBtn) backBtn.classList.add('hidden');
        closeModal(authOverlay);
    }

    // Auth method buttons
    authOverlay.querySelectorAll('[data-auth-method]').forEach(btn => {
        btn.addEventListener('click', () => {
            goToStep(authOverlay, btn.dataset.authMethod);
            if (backBtn) backBtn.classList.remove('hidden');
        });
    });

    // Back button
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            goToStep(authOverlay, '1');
            backBtn.classList.add('hidden');
        });
    }

    // Send email link
    const sendEmailBtn = document.getElementById('authSendEmailBtn');
    if (sendEmailBtn) {
        sendEmailBtn.addEventListener('click', () => {
            const emailInput = document.getElementById('authEmail');
            const sentEmailEl = document.getElementById('authSentEmail');
            if (emailInput && sentEmailEl) {
                sentEmailEl.textContent = emailInput.value || 'your@email.com';
            }
            goToStep(authOverlay, 'email-sent');
        });
    }

    // Close button (remove inline onclick, use JS)
    const closeBtn = authOverlay.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.removeAttribute('onclick');
        closeBtn.addEventListener('click', resetAuth);
    }

    // Close on overlay click
    authOverlay.addEventListener('click', (e) => {
        if (e.target === authOverlay) resetAuth();
    });
}

window.addEventListener('load', initAuthModal);

// --------------------------------------------
// 17. DELIVERY MODAL — форма → успех
// --------------------------------------------
function initDeliveryModal() {
    const deliveryOverlay = document.getElementById('modalDelivery');
    if (!deliveryOverlay) return;

    const form = document.getElementById('deliveryForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            closeModal(deliveryOverlay);
            const successModal = document.getElementById('modalSuccess');
            if (successModal) {
                const title = document.getElementById('successTitle');
                const text = document.getElementById('successText');
                if (title) title.innerHTML = 'Заказ<br>оформлен!';
                if (text) text.textContent = 'Мы свяжемся с вами для подтверждения';
                setTimeout(() => openModal(successModal), 200);
            }
        });
    }

    // Close on overlay click
    deliveryOverlay.addEventListener('click', (e) => {
        if (e.target === deliveryOverlay) closeModal(deliveryOverlay);
    });
}

window.addEventListener('load', initDeliveryModal);

// --------------------------------------------
// 18. DROPDOWN ВЫБОРА РЕГИОНА
// --------------------------------------------
function initRegionDropdown() {
    const dropdown = document.getElementById('regionDropdown');
    const btn = document.getElementById('regionSwitcherBtn');
    const menu = document.getElementById('regionMenu');
    if (!dropdown || !btn || !menu) return;

    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = !menu.classList.contains('hidden');
        if (isOpen) {
            menu.classList.add('hidden');
            dropdown.classList.remove('open');
        } else {
            menu.classList.remove('hidden');
            dropdown.classList.add('open');
        }
    });

    // Закрытие по клику вне dropdown
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) {
            menu.classList.add('hidden');
            dropdown.classList.remove('open');
        }
    });

    // Автопоказ модалки при первом визите (нет cookie)
    const regionModal = document.getElementById('modalRegion');
    if (regionModal && !regionModal.classList.contains('hidden')) {
        openModal(regionModal);
    }
}

// --------------------------------------------
// 19. ВЫПАДАЮЩЕЕ МЕНЮ ЯЗЫКА
// --------------------------------------------
function initLangDropdown() {
    const dropdown = document.getElementById('langDropdown');
    const btn = document.getElementById('langSwitcherBtn');
    const menu = document.getElementById('langMenu');
    if (!dropdown || !btn || !menu) return;

    // Toggle dropdown
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = !menu.classList.contains('hidden');
        if (isOpen) {
            menu.classList.add('hidden');
            dropdown.classList.remove('open');
        } else {
            menu.classList.remove('hidden');
            dropdown.classList.add('open');
        }
    });

    // Выбор языка — ссылки с href уже ведут на /kk/..., /en/..., /ru/...
    // Навигация происходит через обычный переход по <a href>.

    // Закрытие по клику вне dropdown
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) {
            menu.classList.add('hidden');
            dropdown.classList.remove('open');
        }
    });
}

window.addEventListener('load', initRegionDropdown);
window.addEventListener('load', initLangDropdown);