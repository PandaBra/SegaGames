const translations = {
    ru: {
        "site_title": "Sega Online - Играйте в ретро игры",
        "site_header": "Sega Genesis Games",
        "nav_home": "🎮 Игры",
        "nav_feedback": "📝 Отзывы",
        "upload_label": "📂 Загрузить свою игру (.md, .gen)",
        "fullscreen": "⛶ На весь экран",
        "close_game": "Закрыть игру",
        "click_to_start": "Нажмите на игру, чтобы начать.",
        "lang_btn": "EN",
        "site_desc": "Играйте в ретро игры прямо в браузере",
        "games_section": "Список игр",
        "play_btn": "Играть",
        "footer_text": "Sega Online Emulator - 2026",
        "connect_mobile": "Играйте на телефоне:",
        "scan_qr": "Сканируйте QR-код",
        "settings_title": "Настройки",
        "settings_size": "Размер контроллера:",
        "settings_save": "Сохранить",
        "feedback_title": "Отзывы и Предложения",
        "feedback_name": "Ваше имя:",
        "feedback_text": "Ваш отзыв:",
        "feedback_submit": "Отправить",
        "feedback_list": "Последние отзывы",
        "back_to_menu": "Вернуться в меню",
        "exit_game": "Выход",
        "feedback_placeholder_name": "Введите ваше имя",
        "feedback_placeholder_text": "Напишите ваш отзыв здесь...",
        "error_file_not_found": "Ошибка: Файл игры не найден",
        "error_file_desc": "Не удалось загрузить:",
        "error_file_tip": "Убедитесь, что файл существует в папке <b>roms</b>.",
        "game_not_selected": "Игра не выбрана",
        "alert_fullscreen_error": "Ваш браузер не поддерживает полноэкранный режим.",
        "nav_chat": "💬 Чат",
        "chat_header": "Чат Игроков",
        "chat_loading": "Загрузка сообщений...",
        "chat_disclaimer": "Сообщения удаляются автоматически через 24 часа.",
        "chat_send": "Отправить",
        "chat_name_placeholder": "Ваше имя",
        "chat_text_placeholder": "Сообщение..."
    },
    en: {
        "site_title": "Sega Online - Play Retro Games",
        "site_header": "Sega Genesis Games",
        "nav_home": "🎮 Games",
        "nav_feedback": "📝 Feedback",
        "upload_label": "📂 Upload your ROM (.md, .gen)",
        "fullscreen": "⛶ Fullscreen",
        "close_game": "Close Game",
        "click_to_start": "Click on a game to start.",
        "lang_btn": "RU",
        "site_desc": "Play retro games directly in your browser",
        "games_section": "Games List",
        "play_btn": "Play",
        "footer_text": "Sega Online Emulator - 2026",
        "connect_mobile": "Play on mobile:",
        "scan_qr": "Scan QR Code",
        "settings_title": "Settings",
        "settings_size": "Controller Size:",
        "settings_save": "Save",
        "feedback_title": "Feedback & Suggestions",
        "feedback_name": "Your Name:",
        "feedback_text": "Your Feedback:",
        "feedback_submit": "Submit",
        "feedback_list": "Latest Reviews",
        "back_to_menu": "Back to Menu",
        "exit_game": "Exit",
        "feedback_placeholder_name": "Enter your name",
        "feedback_placeholder_text": "Write your feedback here...",
        "error_file_not_found": "Error: Game file not found",
        "error_file_desc": "Could not load:",
        "error_file_tip": "Make sure the file exists in the <b>roms</b> folder.",
        "game_not_selected": "No game selected",
        "alert_fullscreen_error": "Your browser does not support fullscreen mode.",
        "nav_chat": "💬 Chat",
        "chat_header": "Players Chat",
        "chat_loading": "Loading messages...",
        "chat_disclaimer": "Messages are automatically deleted after 24 hours.",
        "chat_send": "Send",
        "chat_name_placeholder": "Your Name",
        "chat_text_placeholder": "Message..."
    }
};

function setLanguage(lang) {
    localStorage.setItem('language', lang);
    document.documentElement.lang = lang;
    
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            if (element.tagName === 'INPUT' && element.type === 'submit') {
                element.value = translations[lang][key];
            } else if (element.tagName === 'INPUT' && element.type === 'button') {
                element.value = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[lang][key]) {
            element.placeholder = translations[lang][key];
        }
    });

    // Update button text
    const langBtns = document.querySelectorAll('#lang-toggle, #lang-toggle-player');
    langBtns.forEach(btn => {
        btn.textContent = lang === 'ru' ? 'EN' : 'RU';
    });
}

function toggleLanguage() {
    const currentLang = localStorage.getItem('language') || 'ru';
    const newLang = currentLang === 'ru' ? 'en' : 'ru';
    setLanguage(newLang);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('language') || 'ru';
    setLanguage(savedLang);

    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) {
        langBtn.addEventListener('click', (e) => {
            e.preventDefault();
            toggleLanguage();
        });
    }
});
