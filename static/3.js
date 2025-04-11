let uploadFiles = new Map();
// 文件输入处理
const fileInput = document.getElementById('fileInput');

function triggerFileInput() {
    fileInput.click();
}

// 文件输入事件监听
fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
        handleFiles({ files: files });
    }
    // 清空文件输入框，允许重复选择同一文件
    fileInput.value = '';
});

// 拖拽区域处理
const dropZone = document.getElementById('dropZone');
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    handleFiles(e.dataTransfer);
});

async function handleFiles(input) {
    const files = input.files;
    const filesList = document.getElementById('uploadFilesList');

    if (!files || files.length === 0) {
        return;
    }

    // 检查总文件数量
    if (uploadFiles.size + files.length > 12) {
        showError('最多只能上传12个文件');
        return;
    }

    // 使用Promise.all并行处理所有文件
    const uploadPromises = Array.from(files).map(async (file) => {
        // 处理拖拽的文件对象
        if (file.kind === 'file') file = file.getAsFile();

        // 检查文件是否重复
        const isDuplicate = Array.from(uploadFiles.values()).some(existingFile =>
            existingFile.file.name === file.name &&
            existingFile.file.size === file.size
        );

        if (isDuplicate) {
            showError(`文件已存在: ${file.name}`);
            return;
        }

        // 检查文件类型
        const validTypes = ['.pdf', '.xps', '.epub', '.fb2', '.cbz', '.mobi'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        if (!validTypes.includes(fileExt)) {
            showError(`不支持的文件格式: ${file.name}`);
            return;
        }

        // 检查文件大小
        if (file.size > 200 * 1024 * 1024) {
            showError(`文件过大: ${file.name}`);
            return;
        }

        // 创建文件ID
        const fileId = Date.now() + Math.random().toString(36).substr(2, 9);

        // 添加到上传列表
        uploadFiles.set(fileId, {
            file: file,
            status: 'pending'
        });

        // 创建并添加文件项UI
        const fileItem = createFileItemUI(fileId, file);
        filesList.appendChild(fileItem);

        // 开始上传
        return uploadFile(fileId);
    });

    // 等待所有文件上传完成
    await Promise.all(uploadPromises);

    // 检查是否有文件上传成功
    if ([...uploadFiles.values()].some(f => f.status === 'success')) {
        document.getElementById('languageSelection').style.display = 'flex';
    }
}

// 创建文件项UI
function createFileItemUI(fileId, file) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.id = `file-${fileId}`;

    const fileName = document.createElement('span');
    fileName.className = 'file-name';
    fileName.textContent = file.name;

    const fileStatus = document.createElement('span');
    fileStatus.className = 'file-status';
    fileStatus.textContent = '准备上传';



    const progressBar = document.createElement('div');
    progressBar.className = 'progress-bar';
    progressBar.style.width = '0%';

    fileItem.appendChild(fileName);
    fileItem.appendChild(fileStatus);

    fileItem.appendChild(progressBar);

    return fileItem;
}

// 移除文件
function removeFile(fileId) {
    const fileItem = document.getElementById(`file-${fileId}`);
    if (fileItem) {
        fileItem.remove();
        uploadFiles.delete(fileId);
    }

    // 如果没有成功上传的文件，隐藏语言选择
    if (![...uploadFiles.values()].some(f => f.status === 'success')) {
        document.getElementById('languageSelection').style.display = 'none';
    }
}

// 上传文件
// async function uploadFile(fileId) {
//     const fileData = uploadFiles.get(fileId);
//     if (!fileData) return;
//
//     const fileItem = document.getElementById(`file-${fileId}`);
//     const statusElement = fileItem.querySelector('.file-status');
//     const progressBar = fileItem.querySelector('.progress-bar');
//
//     try {
//         // 创建 FormData
//         const formData = new FormData();
//         formData.append('file', fileData.file);
//         console.log(formData,'file name')
//
//         // 发送上传请求
//         const response = await fetch('/upload', {
//             method: 'POST',
//             body: formData,
//             onUploadProgress: (progressEvent) => {
//                 const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
//                 progressBar.style.width = percentCompleted + '%';
//                 statusElement.textContent = 'Uploading ' + percentCompleted + '%';
//             }
//         });
//
//         if (response.ok) {
//             statusElement.textContent = 'Upload Success';
//             fileData.status = 'success';
//             console.log(11,fileData.file)
//             progressBar.style.backgroundColor = '#4CAF50';
//         } else {
//             throw new Error('Upload failed');
//         }
//     } catch (error) {
//         statusElement.textContent = 'Upload failure';
//         fileData.status = 'error';
//         progressBar.style.backgroundColor = '#f44336';
//         showError(`Upload failure: ${fileData.file.name}`);
//     }
// }

// 显示错误信息
function showError(message) {
    // 实现错误提示的显示逻辑
    console.error(message);
    // 可以添加一个toast或者其他UI提示
}

function createFileItemUI(fileId, file) {
    const div = document.createElement('div');
    div.className = 'upload-file-item';
    div.id = `file-${fileId}`;

    div.innerHTML = `

        <div class="upload-file-info">
            <div class="upload-file-name">${file.name}</div>
            <div class="upload-file-meta">
                ${formatFileSize(file.size)}
            </div>
        </div>
        <div class="upload-status status-pending">等待上传</div>
    `;

    return div;
}

async function uploadFile(fileId) {
    const fileData = uploadFiles.get(fileId);
    const statusEl = document.querySelector(`#file-${fileId} .upload-status`);

    try {
        statusEl.className = 'upload-status status-uploading';
        statusEl.textContent = 'uploading';

        const formData = new FormData();
        formData.append('file', fileData.file);


        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const result = await response.json();

        statusEl.className = 'upload-status status-success';
        statusEl.textContent = 'Upload Success';
        fileData.status = 'success';

    } catch (error) {
        console.error('Upload error:', error);
        statusEl.className = 'upload-status status-error';
        statusEl.textContent = '上传失败';
        fileData.status = 'error';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showError(message) {
    alert(message);
}

async function handleNextStep() {
    // 获取所有成功上传的文件名
    const successFiles = [...uploadFiles.entries()]
        .filter(([_, data]) => data.status === 'success')
        .map(([_, data]) => data.file.name);

    // 获取选择的语言
    const sourceLang = document.getElementById('sourceLang').value;
    const targetLang = document.getElementById('targetLang').value;

    try {
            const response = await fetch('/config_json')
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // 使用 response.json() 來解析 JSON 數據
            const { translation_services, default_services } = await response.json();
            
            if(translation_services && default_services){
                // 获取当前选择的翻译服务
                const currentTranslationService = default_services.Translation_api;
                
                // 如果当前选择的不是Bing翻译
                if(currentTranslationService !== 'bing'){
                    // 检查当前选择的翻译服务是否配置了API密钥
                    const currentService = translation_services[currentTranslationService];
                    if(!(currentService && (currentService['auth_key'] || currentService['app_key']))){
                        throw new Error('not config translation services authKey');
                    }
                }
            }else{
                throw new Error('data error');
            }
            
            // 1秒后切换界面的Promise
            const switchUIPromise = new Promise((resolve) => {
                setTimeout(() => {
                    document.getElementById('upload_content-1').style.display = 'none';
                    document.getElementById('upload_content-2').style.display = 'flex';
                    resolve();
                }, 1000);
            });


            // 异步发起翻译请求
            fetch('/translation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    files: successFiles,
                    sourceLang: sourceLang,
                    targetLang: targetLang
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // 执行回调函数
                    const value = document.getElementById('record_show_staute').getAttribute('data-value') === 'true';
                    loadArticles(value,false);
                     getecount();


                } else {
                    throw new Error('Translation request failed');
                }
            })
            .catch(error => {
                console.error('Translation request error:', error);
                // showError('翻译请求失败，请稍后重试');
            });

            // 等待1秒后的界面切换
            await switchUIPromise;

        } catch (error) {
        console.error('Error:', error);
        alert(error)
        // showError('操作失败，请稍后重试');
    }


}

 function updatecount() {
    fetch('/config_json')
        .then(response => response.json())
        .then(data => {
           document.getElementById('count_article').textContent += data.count;
        });
    }

function deleteArticle(articleId) {
    // 创建弹窗遮罩层
    const overlay = document.createElement('div');
    console.log(articleId)
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: flex;
        justify-content: center;
        align-items: center;
    `;

    // 创建弹窗内容
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: white;
        border-radius: 8px;
        padding: 24px;
        width: 400px;
        text-align: center;
    `;

    // 创建弹窗标题
    const title = document.createElement('h3');
    title.textContent = 'Delete article';
    title.style.cssText = `
        margin: 0;
        margin-bottom: 8px;
        font-size: 18px;
        color: #333;
    `;

    // 创建弹窗提示文本
    const message = document.createElement('p');
    message.textContent = 'Are you sure you want to delete the selected items? This action cannot be undone.';
    message.style.cssText = `
        margin: 16px 0;
        color: #666;
        font-size: 14px;
    `;

    // 创建按钮容器
    const buttonContainer = document.createElement('div');
    buttonContainer.style.cssText = `
        display: flex;
        justify-content: center;
        gap: 12px;
        margin-top: 24px;
    `;

    // 创建取消按钮
    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.style.cssText = `
        padding: 8px 24px;
        border: none;
        border-radius: 4px;
        background: #f5f5f5;
        color: #333;
        cursor: pointer;
    `;

    // 创建删除按钮
    const confirmButton = document.createElement('button');
    confirmButton.textContent = 'Delete';
    confirmButton.style.cssText = `
        padding: 8px 24px;
        border: none;
        border-radius: 4px;
        background: #ff4d4f;
        color: white;
        cursor: pointer;
    `;

    // 添加按钮点击事件
    cancelButton.onclick = () => {
        document.body.removeChild(overlay);
    };

    confirmButton.onclick = async () => {
        try {
            const response = await fetch('/delete_article', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ articleId })
            });

            if (response.ok) {
                // 删除成功，移除弹窗并刷新页面
                document.body.removeChild(overlay);

                const value = document.getElementById('record_show_staute').getAttribute('data-value') === 'true';
                loadArticles(value,false)
                getecount()
            } else {
                throw new Error('删除失败');
            }
        } catch (error) {
            console.error('删除文章失败:', error);
            alert('删除失败，请重试');
        }
    };

    // 组装弹窗
    buttonContainer.appendChild(cancelButton);
    buttonContainer.appendChild(confirmButton);
    modal.appendChild(title);
    modal.appendChild(message);
    modal.appendChild(buttonContainer);
    overlay.appendChild(modal);

    // 将弹窗添加到页面
    document.body.appendChild(overlay);
}


