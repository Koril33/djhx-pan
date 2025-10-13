// 打开预览
function openPreview(imageUrl) {
    const modal = document.getElementById('imagePreviewModal');
    const previewImage = document.getElementById('previewImage');

    // 设置预览图片的 src
    previewImage.src = imageUrl;
    modal.style.display = "flex"; // 显示预览框
}

function openTextPreview(fileUrl) {
    fetch(fileUrl)
        .then(response => response.text())
        .then(text => {
            const modal = document.getElementById('textPreviewModal');
            const previewContent = document.getElementById('textPreviewContent');

            // 设置文本内容并进行代码高亮
            previewContent.textContent = text;

            modal.style.display = "flex"; // 显示文本预览框
        })
        .catch(error => {
            console.error('Error loading file:', error);
        });
}

function closePreview(event) {
    const modal = document.getElementById('imagePreviewModal');
    const textModal = document.getElementById('textPreviewModal');

    if (event.target === modal || event.target.classList.contains('close')) {
        modal.style.display = "none"; // 隐藏预览框
    }

    if (event.target === textModal || event.target.classList.contains('close')) {
        textModal.style.display = "none"; // 隐藏文本预览框
    }
}

// 图片缩放：鼠标滚轮
let scale = 1;
document.getElementById('previewImage').addEventListener('wheel', function (event) {
    if (event.deltaY > 0) {
        scale *= 0.9; // 缩小
    } else {
        scale *= 1.1; // 放大
    }
    this.style.transform = `scale(${scale})`;
    event.preventDefault(); // 防止页面滚动
});

// 图片旋转：按住右键旋转
let rotate = 0;
document.getElementById('previewImage').addEventListener('contextmenu', function (event) {
    rotate += 90;
    this.style.transform = `scale(${scale}) rotate(${rotate}deg)`;
    event.preventDefault(); // 防止右键菜单出现
});