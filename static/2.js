
// 全局变量存储API密钥
let translationKeys = {
    deepl: '',
    google: '',
    youdao: '',
    aliyun: '',
    tencent: ''
};



// 关闭设置弹窗
function closeSettings() {
    document.getElementById('settingsModal').style.display = 'none';

}
const toggle = document.getElementById('ocrToggle');
const toggle2 = document.getElementById('translationToggle');
function getValue() {
    return toggle.checked ?
           toggle.getAttribute('data-on') :
           toggle.getAttribute('data-off');
}
function getValue2() {
    return toggle2.checked ?
           toggle2.getAttribute('data-on') :
           toggle2.getAttribute('data-off');
}
// 保存设置
async function saveSettings() {
    const saveBtn = document.getElementById('saveBtn');
    const selectedApi = document.querySelector('input[name="api"]:checked');

    if (!selectedApi) {
        alert('请选择一个翻译API');
        return;
    }

    // 获取选中的API和对应的密钥
    const apiType = selectedApi.value;

    console.log(apiType)

    // 更新全局变量
    const value = getValue();
        const value2 = getValue2();
        console.log(value,value2)

// 添加切换事件监听


    try {
        // 发送数据到后端
        console.log(value2,value,'send')
        const response = await fetch('/api/save-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                translation: value2,
                apiType: apiType,
                OCR: value
            })
        });

        if (!response.ok) {
            throw new Error('保存失败');
        }

        // 显示成功状态
        saveBtn.innerHTML = '✓';
        saveBtn.classList.add('success');

        // 2秒后恢复按钮状态
        setTimeout(() => {
            saveBtn.innerHTML = 'Save Settings';
            saveBtn.classList.remove('success');
        }, 2000);



    } catch (error) {
        console.error('保存设置失败:', error);
        alert('保存设置失败，请重试');
    }
}

// 初始化设置
function initSettings() {
    fetch('/api/get-default-services')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data) {
                const settings = data.data;

                // 设置翻译服务选择
                if (settings.translation_service) {
                    document.getElementById(settings.translation_service).checked = true;

                }

                // 设置OCR模式开关
                const ocrToggle = document.getElementById('ocrToggle');
                if (ocrToggle) {
                    ocrToggle.checked = !settings.ocr_modle;
                        console.log(settings.ocr_modle,66)
                }

                // 设置翻译模式开关
                const translationToggle = document.getElementById('translationToggle');
                if (translationToggle) {
                    translationToggle.checked = settings.translation;
                    console.log(settings.translation,77)
                }
                console.log(settings.count)
                document.getElementById('count_article').textContent = ` Articles in Total: ${settings.count} `;
            }
        })
        .catch(error => {
            console.error('获取设置失败:', error);
            alert('获取设置失败，请稍后重试');
        });
}


// 页面加载时初始化设置
document.addEventListener('DOMContentLoaded', initSettings);
