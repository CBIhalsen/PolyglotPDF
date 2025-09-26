// 全局变量存储API密钥
let translationKeys = {
    AI302: '', 
    deepl: '',
    google: '',
    youdao: '',
    aliyun: '',
    tencent: '',
    Grok: '',  // 修改为大写的Grok
    ThirdParty: '',  // 添加ThirdParty
    GLM: '',  // 添加GLM
    bing: ''  // 添加Bing
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
           toggle.getAttribute('data-off');
}


function getecount() {
    fetch('/api/get-default-services')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data) {
                const settings = data.data;

                document.getElementById('count_article').textContent = ` Articles in Total: ${settings.count} `;
            }
        })
        .catch(error => {
            console.error('获取设置失败:', error);
            alert('获取设置失败，请稍后重试');
        });
}



