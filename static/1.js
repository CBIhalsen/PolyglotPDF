
        // 在全局范围定义变量


        // 显示主页
        function showHome() {
            document.getElementById('recentread').innerHTML = 'Recent Reading';
            document.getElementById('articleContainer').style.display = '';
            document.getElementById('viewAllSection').style.display = 'flex';
            document.querySelector('.sidebar-menu a[onclick="showHome()"]').classList.add('active');
            document.querySelector('.sidebar-menu a[onclick="showAllRecent()"]').classList.remove('active');
            document.querySelector('.sidebar-menu a[onclick="showSetup()"]').classList.remove('active'); // 添加这行
            loadArticles(true,true);
              document.getElementById('t-container').style.display = '';
        }

        function showAllRecent() {
            document.getElementById('recentread').innerHTML = 'Recent Reading';

            document.getElementById('articleContainer').style.display = '';
            document.getElementById('viewAllSection').style.display = 'none';
            document.querySelector('.sidebar-menu a[onclick="showHome()"]').classList.remove('active');
            document.querySelector('.sidebar-menu a[onclick="showAllRecent()"]').classList.add('active');
            document.querySelector('.sidebar-menu a[onclick="showSetup()"]').classList.remove('active'); // 添加这行
            loadArticles(false,true);
            document.getElementById('t-container').style.display = '';
        }
        // 添加新的函数处理 Setup steps
        function showSetup() {
            // 隐藏其他部分（如果需要的话）


            document.getElementById('recentread').innerHTML = 'config.json';
            document.getElementById('articleContainer').style.display = 'none';
             document.getElementById('viewAllSection').style.display = 'none';


            // 移除其他菜单项的 active 类
            document.querySelector('.sidebar-menu a[onclick="showHome()"]').classList.remove('active');
            document.querySelector('.sidebar-menu a[onclick="showAllRecent()"]').classList.remove('active');

            // 给 Setup steps 添加 active 类
            document.querySelector('.sidebar-menu a[onclick="showSetup()"]').classList.add('active');
            document.getElementById('t-container').style.display = 'block';
        }

        // 显示上传模态框
        function showUpload() {
            document.getElementById('uploadModal').style.display = 'block';
            document.getElementById('upload_content-1').style.display = 'block';
            document.getElementById('upload_content-2').style.display = 'none';
            document.getElementById('languageSelection').style.display = 'none';

        }



        // 显示设置模态框
        function showSettings() {
            document.getElementById('settingsModal').style.display = 'block';
        }


async function loadArticles(isLimited,first_reload) {
    const container = document.getElementById('articleContainer');
    if (first_reload) {
                const record_show_staute = document.getElementById('record_show_staute');
        record_show_staute.setAttribute('data-value', isLimited);
    }




try {
    container.innerHTML = '<div class="loading">正在加载数据...</div>';

    const response = await fetch('/recent.json');
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    container.innerHTML = '';

    if (data.length === 0) {
        container.innerHTML = '<div class="loading">No reading records yet</div>';
        return;
    }

    // 根据 index 排序(从大到小)
    let sortedArticles = [...data].sort((a, b) => b.index - a.index);

    // 如果需要限制显示数量
    if (isLimited) {
        sortedArticles = sortedArticles.slice(0, 3);
    }

    sortedArticles.forEach(article => {
        const articleCard = document.createElement('a');
        articleCard.className = 'article-card';

        // 上半部分div
        const topDiv = document.createElement('div');
        topDiv.className = 'article-top';
        topDiv.innerHTML = `
            <img src="./static/thumbnail/${article.name.substring(0, article.name.lastIndexOf('.'))}.png" alt="${article.name}">

        `;


        // 下半部分div
        const bottomDiv = document.createElement('div');
        bottomDiv.className = 'article-bottom';

        // 文章标题
        const titleDiv = document.createElement('div');
        titleDiv.className = 'article-title';
        titleDiv.innerHTML = `<h3>${article.name}</h3>`;

        // 信息行div
        const infoDiv = document.createElement('div');
        infoDiv.className = 'article-info';
        infoDiv.innerHTML = `
            <span class="author">${article.author || 'Unknown author'}</span>
            <span class="date">${article.date}</span>
            <span class="language">${article.original_language} - ${article.target_language}</span>
        `;

        bottomDiv.appendChild(titleDiv);
        bottomDiv.appendChild(infoDiv);

        // 状态指示器
        const statusIndicator = document.createElement('div');
        statusIndicator.className = 'status-indicator';

        if (parseInt(article.statue) === 0) {
            statusIndicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            articleCard.className += ' disabled';
            articleCard.addEventListener('click', (e) => {
                e.preventDefault();
                showToast('Translation is not complete yet, unable to view at this time.');
            });
        } else {
            statusIndicator.innerHTML = '<i class="fas fa-check"></i>';
            articleCard.addEventListener('click', () => {
                const targetFileName = `${article.name.replace(/\.pdf$/, '')}_${article.target_language}.pdf`;
                const url = `/pdfviewer.html?name=${encodeURIComponent(article.name)}&name_target_language=${encodeURIComponent(targetFileName)}&index=${encodeURIComponent(article.index)}`;
                window.open(url, '_blank');
            });
            articleCard.style.cursor = 'pointer';

        }
        bottomDiv.appendChild(statusIndicator);

        // 阅读状态标签
        const readStatus = document.createElement('div');
        readStatus.className = `read-status ${parseInt(article.read) === 0 ? 'unread' : 'read'}`;
        readStatus.textContent = parseInt(article.read) === 0 ? 'Unread' : 'Read';

        // 三点菜单按钮
        const menuButton = document.createElement('button');
        menuButton.className = 'menu-button';
        menuButton.innerHTML = '<i class="fas fa-ellipsis-v"></i>';

        articleCard.appendChild(topDiv);
        articleCard.appendChild(bottomDiv);
        articleCard.appendChild(readStatus);
        articleCard.appendChild(menuButton);

        container.appendChild(articleCard);

        // 菜单按钮点击事件
        menuButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            showMenu(e, article, e.currentTarget);
        });
    });
} catch (error) {
    console.error('加载数据失败:', error);
    container.innerHTML = `
        <div class="error">
            加载数据失败，请稍后重试<br>
            <small>${error.message}</small>
        </div>
    `;
}

}

// 显示菜单函数




// Toast提示函数
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 2000);
}


// 显示菜单函数
function showMenu(event, article) {
    const menu = document.createElement('div');
    articleId = article.index
    article_name= article.name
    article_tl = article.target_language
    article_ol = article.original_language
    console.log(2,articleId)
    menu.className = 'article-menu';
    menu.innerHTML = `
        <div class="menu-item" onclick="editArticle(${articleId})">Edit</div>
        <div class="menu-item" onclick="deleteArticle(${articleId})">Delete</div>
       <div class="menu-item" onclick="open_bilingual(${articleId}, '${article_name}', '${article_tl}', '${article_ol}')">Bilingual PDF</div>
    `;

    // 定位菜单
    menu.style.position = 'absolute';
     menu.style.top = `${event.pageY}px`;
     menu.style.left = `${event.pageX}px`;

    document.body.appendChild(menu);

    // 点击其他地方关闭菜单
    document.addEventListener('click', function closeMenu(e) {
        if (!menu.contains(e.target) && e.target !== event.target) {
            menu.remove();
            document.removeEventListener('click', closeMenu);
        }
    });
}


function open_bilingual(articleId,article_name,article_tl,article_ol) {
    const url = `/pdfviewer2.html?name=${encodeURIComponent(article_name)}&target_language=${encodeURIComponent(article_tl)}&index=${encodeURIComponent(articleId)}&original_language=${encodeURIComponent(article_ol)}`;
    window.open(url, '_blank');
}


// Toast提示函数
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 2000);
}



        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            showHome();
        });
function closeUploadModal() {
    // 隐藏modal
    document.getElementById('uploadModal').style.display = 'none';
    // 清空文件列表显示
    document.getElementById('uploadFilesList').innerHTML = '';
    // 清空uploadFiles Map
    uploadFiles.clear();

    // 重置上传界面（如果需要的话）
    document.getElementById('upload_content-1').style.display = 'flex';
    document.getElementById('upload_content-2').style.display = 'none';
}


