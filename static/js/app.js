document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFile = document.getElementById('removeFile');
    const formatSection = document.getElementById('formatSection');
    const targetFormat = document.getElementById('targetFormat');
    const convertBtn = document.getElementById('convertBtn');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    const successSection = document.getElementById('successSection');

    let selectedFile = null;

    const formatCategories = {
        image: ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff'],
        document: ['pdf', 'docx', 'pptx'],
        media: ['mp4', 'avi', 'mkv', 'mov', 'webm', 'mp3', 'wav', 'flac', 'ogg', 'aac']
    };

    function getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showError(message) {
        errorSection.classList.remove('hidden');
        errorSection.classList.add('fade-in');
        errorMessage.textContent = message;
        successSection.classList.add('hidden');
    }

    function hideError() {
        errorSection.classList.add('hidden');
    }

    function showSuccess() {
        successSection.classList.remove('hidden');
        successSection.classList.add('fade-in');
        errorSection.classList.add('hidden');
    }

    function hideSuccess() {
        successSection.classList.add('hidden');
    }

    function resetUI() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.classList.add('hidden');
        formatSection.classList.add('hidden');
        convertBtn.classList.add('hidden');
        progressSection.classList.add('hidden');
        hideError();
        hideSuccess();
        dropZone.classList.remove('hidden');
    }

    async function populateFormats(extension) {
        targetFormat.innerHTML = '<option value="">Select target format...</option>';

        try {
            const response = await fetch(`/api/formats/${extension}`);
            const data = await response.json();

            if (data.available_formats && data.available_formats.length > 0) {
                data.available_formats.forEach(format => {
                    const option = document.createElement('option');
                    option.value = format;
                    option.textContent = format.toUpperCase();
                    targetFormat.appendChild(option);
                });
            } else {
                showError(`No conversion formats available for .${extension} files`);
            }
        } catch (error) {
            let category = null;
            for (const [cat, formats] of Object.entries(formatCategories)) {
                if (formats.includes(extension)) {
                    category = cat;
                    break;
                }
            }

            if (category) {
                formatCategories[category]
                    .filter(f => f !== extension)
                    .forEach(format => {
                        const option = document.createElement('option');
                        option.value = format;
                        option.textContent = format.toUpperCase();
                        targetFormat.appendChild(option);
                    });
            }
        }
    }

    function handleFile(file) {
        if (!file) return;

        selectedFile = file;
        hideError();
        hideSuccess();

        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);

        fileInfo.classList.remove('hidden');
        fileInfo.classList.add('fade-in');
        formatSection.classList.remove('hidden');
        formatSection.classList.add('fade-in');
        convertBtn.classList.remove('hidden');
        convertBtn.classList.add('fade-in');

        const extension = getFileExtension(file.name);
        populateFormats(extension);
    }

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    removeFile.addEventListener('click', resetUI);

    convertBtn.addEventListener('click', async () => {
        if (!selectedFile || !targetFormat.value) {
            showError('Please select a file and target format');
            return;
        }

        hideError();
        hideSuccess();
        convertBtn.disabled = true;
        progressSection.classList.remove('hidden');
        progressSection.classList.add('fade-in');

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('target_format', targetFormat.value);

        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 50);
                progressBar.style.width = percent + '%';
                progressPercent.textContent = percent + '%';
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                progressBar.style.width = '100%';
                progressPercent.textContent = '100%';

                const blob = xhr.response;
                const contentDisposition = xhr.getResponseHeader('Content-Disposition');
                let downloadFilename = `converted_${selectedFile.name.split('.')[0]}.${targetFormat.value}`;

                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                    if (filenameMatch && filenameMatch[1]) {
                        downloadFilename = filenameMatch[1].replace(/['"]/g, '');
                    }
                }

                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = downloadFilename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();

                showSuccess();

                setTimeout(() => {
                    progressSection.classList.add('hidden');
                    convertBtn.disabled = false;
                }, 1500);
            } else {
                try {
                    const errorData = JSON.parse(xhr.responseText);
                    showError(errorData.error || 'Conversion failed');
                } catch {
                    showError('Conversion failed. Please try again.');
                }
                progressSection.classList.add('hidden');
                convertBtn.disabled = false;
            }
        });

        xhr.addEventListener('error', () => {
            showError('Network error. Please check your connection.');
            progressSection.classList.add('hidden');
            convertBtn.disabled = false;
        });

        xhr.open('POST', '/convert');
        xhr.responseType = 'blob';

        let fakeProgress = 50;
        const progressInterval = setInterval(() => {
            if (fakeProgress < 90) {
                fakeProgress += Math.random() * 5;
                progressBar.style.width = fakeProgress + '%';
                progressPercent.textContent = Math.round(fakeProgress) + '%';
            }
        }, 200);

        xhr.addEventListener('loadend', () => {
            clearInterval(progressInterval);
        });

        xhr.send(formData);
    });
});
