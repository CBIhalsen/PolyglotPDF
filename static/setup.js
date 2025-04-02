
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
    document.getElementById('t-count').value = data.count;
        document.getElementById('t-ppc').textContent = data.PPC;
    document.getElementById('t-ppc').value = data.PPC;
document.getElementById('count_article').textContent += data.count;


    console.log('count', data.count);

    // 初始化翻译服务 (这部分代码保持不变)
    const translationServices = document.getElementById('t-translation-services');
    Object.entries(data.translation_services).forEach(([service, config]) => {
        const serviceDiv = createServiceSection(service, config);
        translationServices.appendChild(serviceDiv);
    });

    // 初始化OCR服务 (这部分代码保持不变)
    const ocrServices = document.getElementById('t-ocr-services');
    Object.entries(data.ocr_services).forEach(([service, config]) => {
        const serviceDiv = createServiceSection(service, config);
        ocrServices.appendChild(serviceDiv);
    });

    // 初始化默认配置
    const defaultServices = document.getElementById('t-default-services');
    console.log('api',data.default_services.Translation_api)
    const defaultConfig = {
        'ocr_model': {
            type: 'select',
            options: ['true', 'false'],
            value: data.default_services.ocr_model
        },
        'Enable_translation': {
            type: 'select',
            options: ['true', 'false'],
            value: data.default_services.Enable_translation
        },
        'Translation_api': {
            type: 'select',
            options: ['Doubao', 'Qwen', 'deepseek', 'openai', 'deepL', 'youdao'],
            value: data.default_services.Translation_api
        }
    };

    // 在 initializeUI 函数中修改相关部分
Object.entries(defaultConfig).forEach(([key, config]) => {
    const inputGroup = document.createElement('div');
    inputGroup.className = 't-input-group';

    const select = document.createElement('select');
    select.className = 't-input';

    config.options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;

        // 修改选项匹配逻辑
        if (key === 'Translation_api') {
            // 直接比较字符串值
            optionElement.selected = (option === config.value);
            console.log(`Translation API option: ${option}, config value: ${config.value}, selected: ${optionElement.selected}`);
        }  else if (key === 'ocr_model' || key === 'Enable_translation' ) {
                const optionBool = option.toLowerCase() === 'true';
                optionElement.selected = (optionBool === config.value);
            }

        select.appendChild(optionElement);
    });
      if (key === 'Enable_translation') {
        inputGroup.innerHTML = `<label style="font-size: 80%; font-weight: bold;">${key}:</label>`;
      } else {
        inputGroup.innerHTML = `<label>${key}:</label>`;
      }


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
async function saveall() {
    const saveall = document.getElementById('saveall');


// 添加切换事件监听


    try {
        // 发送数据到后端

        const config = collectConfig();

        const response = await fetch('/save_all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
             body: JSON.stringify(config)
        });

        if (!response.ok) {
            throw new Error('保存失败');
        }

        // 显示成功状态
        saveall.innerHTML = '✓';
        saveall.classList.add('success');

        // 2秒后恢复按钮状态
        setTimeout(() => {
            saveall.innerHTML = '保存所有修改';
            saveall.classList.remove('success');
        }, 2000);



    } catch (error) {
        console.error('保存设置失败:', error);
        alert('保存设置失败，请重试');
    }
}
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
      count: document.getElementById('t-count').value,
        PPC: parseInt(document.getElementById('t-ppc').value, 10),
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
// 收集默认配置
        const defaultServices = document.getElementById('t-default-services');
        [...defaultServices.getElementsByClassName('t-input-group')].forEach(group => {
            const key = group.querySelector('label').textContent.replace(':', '');
            let value = group.querySelector('select').value;

            // 对特定key进行布尔值转换
            if(key === 'ocr_model' || key === 'Enable_translation' ) {
                value = value === 'true' ? true : false;
            }


            config.default_services[key] = value;
        });


    return config;
}

