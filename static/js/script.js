// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // 文件选择显示
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            fileName.textContent = this.files[0]?.name || '';
        });

        // 上传表单提交处理
        document.querySelector('form').addEventListener('submit', function(e) {
            const submitBtn = document.querySelector('.upload-submit');
            if (fileInput.files.length === 0) {
                e.preventDefault();
                return;
            }

            submitBtn.innerHTML = '<div class="loading-spinner"></div> 上传中...';
            submitBtn.disabled = true;
        });
    }

    // 移动端优化：自动隐藏键盘在文件选择后
    if (/Mobi|Android/i.test(navigator.userAgent)) {
        if (fileInput) {
            fileInput.addEventListener('focus', function() {
                this.blur();
            });
        }
    }
});