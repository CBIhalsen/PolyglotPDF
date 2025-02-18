
    // 页面加载时获取配置
    fetch('/config_json')
        .then(response => response.json())
        .then(data => {
            initializeUI(data);
        });

    // 初始化UI
  // 初始化UI
function initializeUI(data) {
    document.getElementById('t-count').textContent = data.count;

    // 初始化翻译服务
    const translationServices = document.getElementById('t-translation-services');
    Object.entries(data.translation_services).forEach(([service, config]) => {
        const serviceDiv = createServiceSection(service, config);
        translationServices.appendChild(serviceDiv);
    });

    // 初始化OCR服务
    const ocrServices = document.getElementById('t-ocr-services');
    Object.entries(data.ocr_services).forEach(([service, config]) => {
        const serviceDiv = createServiceSection(service, config);
        ocrServices.appendChild(serviceDiv);
    });

    // 初始化默认配置
    const defaultServices = document.getElementById('t-default-services');
    const defaultConfig = {
        'ocr_modle': {
            type: 'select',
            options: ['true', 'false'],
            value: data.default_services.ocr_modle
        },
        'Enable_translation': {
            type: 'select',
            options: ['true', 'false'],
            value: data.default_services.translation
        },
        'Translation_api': {
            type: 'select',
            options: ['Doubao', 'Qwen', 'Deepseek', 'Openai', 'DeepL', 'Youdao'],
            value: data.default_services.translation_service
        }
    };

    Object.entries(defaultConfig).forEach(([key, config]) => {
        const inputGroup = document.createElement('div');
        inputGroup.className = 't-input-group';

        const select = document.createElement('select');
        select.className = 't-input';

        config.options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            if(option === config.value) {
                optionElement.selected = true;
            }
            select.appendChild(optionElement);
        });

        inputGroup.innerHTML = `<label>${key}:</label>`;
        inputGroup.appendChild(select);
        defaultServices.appendChild(inputGroup);
    });
}


    // 创建服务配置区域
    function createServiceSection(serviceName, config) {
        const section = document.createElement('div');
        section.className = 't-sub-section';

        const header = document.createElement('div');
        header.className = 't-section-header';
        header.innerHTML = `
            <h4>${serviceName}</h4>
            <button class="t-toggle-btn">+</button>
        `;

        const content = document.createElement('div');
        content.className = 't-content';

        Object.entries(config).forEach(([key, value]) => {
            const inputGroup = document.createElement('div');
            inputGroup.className = 't-input-group';
            inputGroup.innerHTML = `
                <label>${key}:</label>
                <input type="text" class="t-input" value="${value}">
            `;
            content.appendChild(inputGroup);
        });

        section.appendChild(header);
        section.appendChild(content);

        return section;
    }

    // 添加展开/折叠功能
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('t-toggle-btn')) {
            const button = e.target;
            const content = button.closest('.t-section-header').nextElementSibling;
            button.classList.toggle('t-active');
            content.classList.toggle('t-active');
        }
    });

    // 添加自动保存功能
    let saveTimeout;
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('t-input')) {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                // 收集当前所有配置数据
                const config = collectConfig();
                // 发送到后端
                fetch('/update_config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(config)
                });
            }, 5000);
        }
    });

    // 保存所有修改
    document.querySelector('.t-save-btn').addEventListener('click', function() {
        const config = collectConfig();
        fetch('/save_all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
    });

    // 收集所有配置数据
    // 收集所有配置数据
function collectConfig() {
    const config = {
        count: document.getElementById('t-count').textContent,
        translation_services: {},
        ocr_services: {},
        default_services: {}
    };

    // 收集翻译服务配置
    const translationServices = document.getElementById('t-translation-services');
    [...translationServices.getElementsByClassName('t-sub-section')].forEach(section => {
        const serviceName = section.querySelector('h4').textContent;
        config.translation_services[serviceName] = {};
        [...section.getElementsByClassName('t-input-group')].forEach(group => {
            const key = group.querySelector('label').textContent.replace(':', '');
            const value = group.querySelector('input').value;
            config.translation_services[serviceName][key] = value;
        });
    });

    // 收集OCR服务配置
    const ocrServices = document.getElementById('t-ocr-services');
    [...ocrServices.getElementsByClassName('t-sub-section')].forEach(section => {
        const serviceName = section.querySelector('h4').textContent;
        config.ocr_services[serviceName] = {};
        [...section.getElementsByClassName('t-input-group')].forEach(group => {
            const key = group.querySelector('label').textContent.replace(':', '');
            const value = group.querySelector('input').value;
            config.ocr_services[serviceName][key] = value;
        });
    });

    // 收集默认配置
    const defaultServices = document.getElementById('t-default-services');
    [...defaultServices.getElementsByClassName('t-input-group')].forEach(group => {
        const key = group.querySelector('label').textContent.replace(':', '');
        const value = group.querySelector('select').value;
        config.default_services[key] = value;
    });

    return config;
}

