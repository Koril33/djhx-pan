// 切换暗黑模式
function toggleDark() {
    document.body.classList.toggle('dark');
    localStorage.setItem('darkMode', document.body.classList.contains('dark'));
}


// 导航相关函数（保持不变）
function updateNavRightPosition() {
    const navLeft = document.querySelector('.nav-left');
    const navRight = document.querySelector('.nav-right');

    if (!navLeft || !navRight) return;

    const height = navLeft.offsetHeight;
    navRight.style.top = `calc(100% + ${height}px)`;
}


function toggleNav() {
    document.body.classList.toggle('nav-open');
    setTimeout(updateNavRightPosition, 10);
}


// 切换目录下拉菜单
function toggleChapterDropdown() {
    const dropdownMenu = document.querySelector('.chapter-dropdown .dropdown-menu');
    if (dropdownMenu) {
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    }
}


window.addEventListener('load', updateNavRightPosition);
window.addEventListener('resize', updateNavRightPosition);
// 页面加载完成后恢复所有用户偏好
document.addEventListener('DOMContentLoaded', () => {
    // 恢复暗黑模式
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark');
    }

    const toggle = document.querySelector('.dropdown-toggle');
    if (toggle) {
        toggle.addEventListener('click', (e) => {
            e.stopPropagation(); // 阻止立即关闭
            toggleChapterDropdown();
        });
    }
});
