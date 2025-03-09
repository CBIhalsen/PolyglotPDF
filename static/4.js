
// 用于存储批量选择的文章ID
let selectedBatchIds = new Set();

// 展示批量管理弹窗
function showBatchModal() {
  document.getElementById('batchModal').style.display = 'block';
  loadBatchData(); // 获取数据并渲染卡片
}

// 关闭批量管理弹窗
function closeBatchModal() {
  document.getElementById('batchModal').style.display = 'none';
  // 关闭时清空已选
  selectedBatchIds.clear();
}

// 加载 recent.json 数据并渲染到批量弹窗
async function loadBatchData() {
  const container = document.getElementById('batchGrid');
  container.innerHTML = '<div class="loading">Loading data...</div>';
  try {
    const response = await fetch('/recent.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    container.innerHTML = '';

    if (!data || data.length === 0) {
      container.innerHTML = '<div class="loading">No records to batch manage</div>';
      return;
    }

    // 按 index 倒序
    const sortedData = data.sort((a, b) => b.index - a.index);

    // 将卡片渲染到 container
    sortedData.forEach(item => {
      const card = document.createElement('div');
      card.className = 'batch-card';
      card.dataset.indexId = item.index; // 存一下，方便后续操作

      // 已读 / 未读
      const readStatus = item.read === "1" ? "Read" : "Unread";

      // 注意：后端返回没有作者的话，可以用Unknown
      const author = item.author || "Unknown author";
      const original_lan = item.original_language ;
      const target_lan = item.target_language;

      card.innerHTML = `
        <div class="batch-card-title"><strong>${item.name}</strong></div>
        <div class="batch-card-info">
          <p>Date: ${item.date}</p>
          <p>Author: ${author}</p>
          <p>Status: ${readStatus}  ||  Convertion: 

${original_lan} to ${target_lan}</p>
     
        </div>
      `;

      // 点击选择或取消选择
      card.addEventListener('click', () => {
        if (selectedBatchIds.has(item.index)) {
          selectedBatchIds.delete(item.index);
          card.classList.remove('selected');
        } else {
          selectedBatchIds.add(item.index);
          card.classList.add('selected');
        }
      });

      container.appendChild(card);
    });
  } catch (error) {
    console.error('加载数据失败:', error);
    container.innerHTML = `<div class="error">Failed to load data<br>${error.message}</div>`;
  }
}

// 全选 / 取消全选
function toggleSelectAll() {
  const container = document.getElementById('batchGrid');
  const cards = container.querySelectorAll('.batch-card');

  // 如果有一个未选，则本次点击后全选，否则取消全选
  let shouldSelectAll = false;
  if (selectedBatchIds.size < cards.length) {
    // 还有没选的，进行全选
    shouldSelectAll = true;
  }

  cards.forEach(card => {
    const indexId = parseInt(card.dataset.indexId, 10);
    if (shouldSelectAll) {
      selectedBatchIds.add(indexId);
      card.classList.add('selected');
    } else {
      selectedBatchIds.delete(indexId);
      card.classList.remove('selected');
    }
  });
}

// 批量删除
async function handleBatchDelete() {
  if (selectedBatchIds.size === 0) {
    alert('No articles selected!');
    return;
  }

  // 简单确认
  if (!confirm('Are you sure you want to delete the selected items?')) {
    return;
  }

  // 发送到后端
  try {
    // 假设后端你新加了一个 /delete_batch 接口
    const response = await fetch('/delete_batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        articleIds: Array.from(selectedBatchIds)
      })
    });

    if (!response.ok) throw new Error('Delete failed');

    // 删除成功后刷新弹窗数据
    selectedBatchIds.clear();
    loadBatchData();
    getecount();
  } catch (error) {
    console.error('删除失败:', error);
    alert('Delete failed, please try again!');
  }
}

// 生成思维导图
function handleMindMap() {
  if (selectedBatchIds.size === 0) {
    alert('No articles selected for mind map!');
    return;
  }

  // 这里演示直接在控制台输出，你可以改为实际的请求
  console.log('生成思维导图，选中的ID:', Array.from(selectedBatchIds));
  alert('Pretend to generate Mind Map for selected items');
}

// 总结
function handleSummary() {
  if (selectedBatchIds.size === 0) {
    alert('No articles selected for summary!');
    return;
  }

  // 同上，这里可以改成实际的后端接口
  console.log('生成总结，选中的ID:', Array.from(selectedBatchIds));
  alert('Pretend to generate Summary for selected items');
}
