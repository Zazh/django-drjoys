(() => {
  // src/js/main.js
  function initMobileMenu() {
    const menuBtn = document.getElementById("menuBtn");
    const mainNav = document.getElementById("mainNav");
    const siteHeader = document.querySelector(".site-header");
    const navWrapper = document.querySelector(".nav_wrapper");
    if (!menuBtn || !mainNav || !siteHeader || !navWrapper) return;
    let isMenuActive = false;
    let youtubePlayer = null;
    const isDesktop = window.matchMedia("(min-width: 1024px)");
    function initYouTubePlayer() {
      if (typeof YT === "undefined" || typeof YT.Player === "undefined") {
        console.warn("YouTube API \u043D\u0435 \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043D");
        return;
      }
      youtubePlayer = new YT.Player("navYoutubeVideo", {
        events: {
          "onReady": onPlayerReady
        }
      });
    }
    function onPlayerReady(event) {
      console.log("YouTube player \u0433\u043E\u0442\u043E\u0432");
    }
    function playVideo() {
      if (youtubePlayer && youtubePlayer.playVideo) {
        youtubePlayer.mute();
        youtubePlayer.playVideo();
      }
    }
    function pauseVideo() {
      if (youtubePlayer && youtubePlayer.pauseVideo) {
        youtubePlayer.pauseVideo();
      }
    }
    menuBtn.addEventListener("click", () => {
      isMenuActive = !isMenuActive;
      const lines = menuBtn.querySelectorAll("span");
      if (isMenuActive) {
        lines[0].style.opacity = "0";
        lines[1].style.transform = "rotate(45deg)";
        lines[2].style.transform = "rotate(-45deg)";
        lines[3].style.opacity = "0";
        mainNav.classList.remove("hidden");
        navWrapper.classList.add("bottom-0");
        navWrapper.classList.remove("backdrop-blur-xs");
        navWrapper.classList.add("backdrop-blur-xl");
        setTimeout(() => {
          playVideo();
        }, 300);
      } else {
        lines[0].style.opacity = "1";
        lines[1].style.transform = "rotate(0deg)";
        lines[2].style.transform = "rotate(0deg)";
        lines[3].style.opacity = "1";
        mainNav.classList.add("hidden");
        navWrapper.classList.remove("bottom-0");
        navWrapper.classList.remove("backdrop-blur-xl");
        navWrapper.classList.add("backdrop-blur-xs");
        pauseVideo();
      }
    });
    isDesktop.addEventListener("change", (e) => {
    });
    if (window.YT && window.YT.Player) {
      initYouTubePlayer();
    } else {
      window.onYouTubeIframeAPIReady = function() {
        initYouTubePlayer();
      };
    }
  }
  window.addEventListener("load", initMobileMenu);
  function updateProductGridGap() {
    const referenceCol = document.getElementById("referenceCol");
    const productGrid = document.getElementById("productGrid");
    if (!referenceCol || !productGrid) return;
    const isXlOrLarger = window.matchMedia("(min-width: 1280px)");
    if (!isXlOrLarger.matches) {
      productGrid.style.gap = "";
      return;
    }
    if (referenceCol.classList.contains("hidden")) {
      productGrid.style.gap = "";
      return;
    }
    const colWidth = referenceCol.offsetWidth;
    productGrid.style.gap = `${colWidth}px`;
  }
  window.addEventListener("load", updateProductGridGap);
  var resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(updateProductGridGap, 100);
  });
  function initProductImageSlider() {
    const productCards = document.querySelectorAll(".product-card_picture");
    productCards.forEach((card) => {
      const images = card.querySelectorAll(".product-image");
      const imagesCount = images.length;
      if (imagesCount <= 1) return;
      const indicatorsContainer = card.querySelector(".product-indicators");
      indicatorsContainer.innerHTML = "";
      const indicators = [];
      for (let i = 0; i < imagesCount; i++) {
        const indicator = document.createElement("span");
        indicator.classList.add("indicator");
        indicatorsContainer.appendChild(indicator);
        indicators.push(indicator);
      }
      images[0].classList.add("active");
      indicators[0].classList.add("active");
      let currentIndex = 0;
      let touchStartX = 0;
      let touchEndX = 0;
      function showImage(index) {
        if (index === currentIndex) return;
        images.forEach((img) => img.classList.remove("active"));
        indicators.forEach((ind) => ind.classList.remove("active"));
        images[index].classList.add("active");
        indicators[index].classList.add("active");
        currentIndex = index;
      }
      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const sectionWidth = rect.width / imagesCount;
        const newIndex = Math.floor(x / sectionWidth);
        if (newIndex >= 0 && newIndex < imagesCount) {
          showImage(newIndex);
        }
      });
      card.addEventListener("mouseleave", () => {
        showImage(0);
      });
      card.addEventListener("touchstart", (e) => {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });
      card.addEventListener("touchend", (e) => {
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
  window.addEventListener("load", initProductImageSlider);
  function initHeartbeat() {
    const heartElement = document.querySelector(".heart-beat");
    const dotElement = document.querySelector(".dot-shake");
    const triggers = document.querySelectorAll(".heart-trigger");
    if (!heartElement || triggers.length === 0) return;
    let hoverTimer = null;
    let scaleValue = 1;
    let shakeIntensity = 1;
    let isHovering = false;
    let animationFrame = null;
    function updateScale() {
      if (!isHovering) return;
      const elapsed = Date.now() - hoverTimer;
      const totalDuration = 2e4;
      const progress = Math.min(elapsed / totalDuration, 1);
      if (progress < 0.2) {
        const localProgress = progress / 0.2;
        scaleValue = 1 + localProgress * 0.05;
        shakeIntensity = 1 + localProgress * 0.5;
      } else if (progress < 0.5) {
        const localProgress = (progress - 0.2) / 0.3;
        scaleValue = 1.05 + localProgress * 0.05;
        shakeIntensity = 1.5 + localProgress * 0.5;
      } else if (progress < 0.8) {
        const localProgress = (progress - 0.5) / 0.3;
        scaleValue = 1.1 + localProgress * 0.05;
        shakeIntensity = 2 + localProgress * 0.5;
      } else {
        const localProgress = (progress - 0.8) / 0.2;
        scaleValue = 1.15 + localProgress * 0.2;
        shakeIntensity = 2.5 + localProgress * 0.5;
      }
      if (elapsed >= totalDuration) {
        hoverTimer = Date.now();
      }
      heartElement.style.setProperty("--heart-scale", scaleValue);
      if (dotElement) {
        dotElement.style.setProperty("--shake-intensity", shakeIntensity);
      }
      animationFrame = requestAnimationFrame(updateScale);
    }
    triggers.forEach((trigger) => {
      trigger.addEventListener("mouseenter", () => {
        isHovering = true;
        hoverTimer = Date.now();
        scaleValue = 1;
        shakeIntensity = 1;
        heartElement.classList.add("is-beating");
        if (dotElement) {
          dotElement.classList.add("is-shaking");
        }
        animationFrame = requestAnimationFrame(updateScale);
      });
      trigger.addEventListener("mouseleave", () => {
        isHovering = false;
        heartElement.classList.remove("is-beating");
        heartElement.style.setProperty("--heart-scale", 1);
        if (dotElement) {
          dotElement.classList.remove("is-shaking");
          dotElement.style.setProperty("--shake-intensity", 1);
        }
        if (animationFrame) {
          cancelAnimationFrame(animationFrame);
          animationFrame = null;
        }
      });
    });
  }
  window.addEventListener("load", initHeartbeat);
  function initFAQ() {
    const faqItems = document.querySelectorAll(".faq-item");
    if (faqItems.length === 0) return;
    faqItems.forEach((item, index) => {
      const button = item.querySelector(".faq-button");
      const panel = item.querySelector(".faq-panel");
      if (!button || !panel) return;
      const buttonId = `faq-button-${index + 1}`;
      const panelId = `faq-panel-${index + 1}`;
      button.id = buttonId;
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-controls", panelId);
      panel.id = panelId;
      panel.setAttribute("role", "region");
      panel.setAttribute("aria-labelledby", buttonId);
      button.addEventListener("click", () => {
        const isExpanded = button.getAttribute("aria-expanded") === "true";
        faqItems.forEach((otherItem) => {
          const otherButton = otherItem.querySelector(".faq-button");
          const otherPanel = otherItem.querySelector(".faq-panel");
          if (otherButton !== button) {
            otherButton.setAttribute("aria-expanded", "false");
            otherPanel.classList.remove("is-open");
          }
        });
        if (isExpanded) {
          button.setAttribute("aria-expanded", "false");
          panel.classList.remove("is-open");
        } else {
          button.setAttribute("aria-expanded", "true");
          panel.classList.add("is-open");
        }
      });
    });
  }
  window.addEventListener("load", initFAQ);
  function initAddToCart() {
    const addToCartBlocks = document.querySelectorAll(".add-to-cart");
    if (addToCartBlocks.length === 0) return;
    addToCartBlocks.forEach((block) => {
      const button = block.querySelector(".btn-cat");
      const buttonWrapper = block.querySelector(".cart-button-wrapper");
      const linksWrapper = block.querySelector(".cart-links-wrapper");
      if (!button || !buttonWrapper || !linksWrapper) return;
      button.addEventListener("click", (e) => {
        e.stopPropagation();
        addToCartBlocks.forEach((otherBlock) => {
          if (otherBlock !== block) {
            const otherButtonWrapper = otherBlock.querySelector(".cart-button-wrapper");
            const otherLinksWrapper = otherBlock.querySelector(".cart-links-wrapper");
            otherBlock.classList.remove("active");
            otherButtonWrapper.classList.remove("hidden");
            otherLinksWrapper.classList.add("hidden");
          }
        });
        block.classList.add("active");
        buttonWrapper.classList.add("hidden");
        linksWrapper.classList.remove("hidden");
      });
      document.addEventListener("click", (e) => {
        if (!block.contains(e.target)) {
          block.classList.remove("active");
          buttonWrapper.classList.remove("hidden");
          linksWrapper.classList.add("hidden");
        }
      });
      block.addEventListener("click", (e) => {
        e.stopPropagation();
      });
    });
  }
  window.addEventListener("load", initAddToCart);
  function initProductSlider() {
    const sliders = document.querySelectorAll(".product-slider");
    if (sliders.length === 0) return;
    sliders.forEach((slider) => {
      const images = slider.querySelectorAll(".slider-image");
      const indicatorsContainer = slider.querySelector(".slider-indicators");
      const playPauseBtn = slider.querySelector(".slider-play-pause");
      const pauseIcon = playPauseBtn?.querySelector(".pause-icon");
      const playIcon = playPauseBtn?.querySelector(".play-icon");
      const progressBar = slider.querySelector(".progress-bar");
      const imagesCount = images.length;
      if (imagesCount <= 1) return;
      indicatorsContainer.innerHTML = "";
      const indicators = [];
      for (let i = 0; i < imagesCount; i++) {
        const indicator = document.createElement("span");
        indicator.classList.add("indicator");
        indicatorsContainer.appendChild(indicator);
        indicators.push(indicator);
      }
      const autoplay = slider.getAttribute("data-autoplay") === "true";
      const interval = parseInt(slider.getAttribute("data-interval")) || 5e3;
      let currentIndex = 0;
      let autoplayTimer = null;
      let progressTimer = null;
      let isPlaying = autoplay;
      let isHovered = false;
      function showImage(index) {
        images.forEach((img) => img.classList.remove("active"));
        indicators.forEach((ind) => ind.classList.remove("active"));
        images[index].classList.add("active");
        indicators[index].classList.add("active");
        currentIndex = index;
      }
      function nextImage() {
        const nextIndex = (currentIndex + 1) % imagesCount;
        showImage(nextIndex);
      }
      function updateProgress() {
        if (!isPlaying || isHovered) return;
        let progress = 0;
        const step = 100 / (interval / 100);
        progressTimer = setInterval(() => {
          if (isHovered) return;
          progress += step;
          const offset = 100 - progress;
          progressBar.style.strokeDashoffset = offset;
          if (progress >= 100) {
            clearInterval(progressTimer);
          }
        }, 100);
      }
      function startAutoplay() {
        if (!isPlaying || isHovered) return;
        stopAutoplay();
        progressBar.style.strokeDashoffset = 100;
        updateProgress();
        autoplayTimer = setTimeout(() => {
          if (isHovered) return;
          nextImage();
          startAutoplay();
        }, interval);
      }
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
      function togglePlayPause() {
        isPlaying = !isPlaying;
        if (isPlaying) {
          pauseIcon.classList.remove("hidden");
          playIcon.classList.add("hidden");
          playPauseBtn.setAttribute("aria-label", "Pause slideshow");
          if (!isHovered) {
            startAutoplay();
          }
        } else {
          pauseIcon.classList.add("hidden");
          playIcon.classList.remove("hidden");
          playPauseBtn.setAttribute("aria-label", "Play slideshow");
          stopAutoplay();
          progressBar.style.strokeDashoffset = 100;
        }
      }
      showImage(0);
      if (autoplay) {
        startAutoplay();
      }
      if (playPauseBtn) {
        playPauseBtn.addEventListener("click", (e) => {
          e.stopPropagation();
          togglePlayPause();
        });
      }
      slider.addEventListener("mouseenter", () => {
        isHovered = true;
        stopAutoplay();
      });
      slider.addEventListener("mouseleave", () => {
        isHovered = false;
        if (isPlaying) {
          startAutoplay();
        }
      });
      slider.addEventListener("click", (e) => {
        if (e.target.closest(".slider-play-pause")) return;
        if (window.innerWidth < 1024) {
          togglePlayPause();
        }
      });
      let touchStartX = 0;
      let touchEndX = 0;
      slider.addEventListener("touchstart", (e) => {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });
      slider.addEventListener("touchend", (e) => {
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
  window.addEventListener("load", initProductSlider);
  function initDragCarousel() {
    const carouselWrappers = document.querySelectorAll(".carousel-wrapper");
    if (carouselWrappers.length === 0) return;
    carouselWrappers.forEach((wrapper) => {
      const cursor = wrapper.querySelector(".carousel-cursor");
      if (!cursor) return;
      let isDragging = false;
      let startX = 0;
      let scrollLeft = 0;
      let hasMoved = false;
      function updateCursorPosition(e) {
        cursor.style.left = e.clientX + "px";
        cursor.style.top = e.clientY + "px";
      }
      function startDrag(e) {
        isDragging = true;
        hasMoved = false;
        wrapper.classList.add("is-dragging");
        startX = e.pageX - wrapper.offsetLeft;
        scrollLeft = wrapper.scrollLeft;
        wrapper.style.scrollBehavior = "auto";
        e.preventDefault();
      }
      function drag(e) {
        if (!isDragging) return;
        e.preventDefault();
        hasMoved = true;
        const x = e.pageX - wrapper.offsetLeft;
        const walk = (x - startX) * 1.5;
        wrapper.scrollLeft = scrollLeft - walk;
      }
      function endDrag(e) {
        if (!isDragging) return;
        isDragging = false;
        if (hasMoved) {
          setTimeout(() => {
            wrapper.classList.remove("is-dragging");
          }, 10);
        } else {
          wrapper.classList.remove("is-dragging");
        }
        wrapper.style.scrollBehavior = "smooth";
      }
      wrapper.addEventListener("mousemove", (e) => {
        updateCursorPosition(e);
        if (isDragging) {
          drag(e);
        }
      });
      wrapper.addEventListener("mousedown", startDrag);
      wrapper.addEventListener("mouseup", endDrag);
      wrapper.addEventListener("mouseleave", endDrag);
      wrapper.addEventListener("click", (e) => {
        if (hasMoved) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          hasMoved = false;
        }
      }, true);
    });
  }
  window.addEventListener("load", initDragCarousel);
})();
